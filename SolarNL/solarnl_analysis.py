"""Reproducible private SolarNL analysis pipeline.

Requires a local, authorized Datasheet_query_(10).csv and KNMI hourly CSV.
Nothing in this module writes raw or derived data to the public repository.
"""
from pathlib import Path
from itertools import combinations
import numpy as np
import pandas as pd
try:
    import statsmodels.formula.api as smf
except ImportError:  # panel-specific core analysis below only needs NumPy/pandas
    smf=None
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:  # Plotly is only needed when notebook figures are built
    px=go=None

HERE=Path(__file__).resolve().parent
RAW=HERE/'Datasheet_query_(10).csv'
KNMI_FILE=HERE/'knmi_hourly.csv'


def load_influx_export(path=RAW):
    tables=[]; current=[]
    with path.open(encoding='utf-8-sig') as f:
        for line in f:
            if line.startswith('#datatype'):
                if current: tables.append(current)
                current=[]
            elif not line.startswith('#') and line.strip(): current.append(line)
    if current: tables.append(current)
    frames=[]
    for lines in tables:
        d=pd.read_csv(__import__('io').StringIO(''.join(lines)))
        d=d.loc[:,~d.columns.astype(str).str.startswith('Unnamed')]
        d=d.drop(columns=['result','table','_start','_stop'],errors='ignore').dropna(how='all')
        if '_time' in d: d['_time']=pd.to_datetime(d['_time'],utc=True,errors='coerce')
        frames.append(d)
    solar=pd.concat([x for x in frames if 'impp' in x.columns],ignore_index=True)
    weather=pd.concat([x for x in frames if 'Temperature-PVMET500' in x.columns],ignore_index=True)
    return solar,weather


def load_knmi(path=KNMI_FILE):
    cols=['STN','YYYYMMDD','HH','T','Q','N','U','FH','RH','WW']
    k=pd.read_csv(path,comment='#',names=cols,skipinitialspace=True,header=None)
    k=k[pd.to_numeric(k.STN,errors='coerce').notna()].copy()
    k['STN']=k.STN.astype(int)
    k['time']=(pd.to_datetime(k.YYYYMMDD.astype(str),format='%Y%m%d')+
               pd.to_timedelta(pd.to_numeric(k.HH),unit='h')).dt.tz_localize('UTC')
    for c in ['T','Q','N','U','FH','RH','WW']: k[c]=pd.to_numeric(k[c],errors='coerce')
    k=k.rename(columns={'T':'T_air_knmi_C','Q':'Q_J_cm2','N':'cloud_oktas','U':'RH_pct','FH':'wind_tenths_ms','RH':'rain_tenths_mm','WW':'weather_code'})
    k['T_air_knmi_C']/=10
    # Q is an hourly energy integral: 1 J/cm² = 10,000 J/m²; divide by 3600 s.
    k['G_knmi_Wm2']=k['Q_J_cm2']*(10000/3600)
    k['wind_ms']=k['wind_tenths_ms']/10
    k['rain_mm']=k['rain_tenths_mm'].where(k['rain_tenths_mm']>=0)/10
    k['rain_flag']=k['rain_tenths_mm']>0
    k['cloud_class']=pd.cut(k.cloud_oktas.where(k.cloud_oktas<=8),[-.1,2,5,8],labels=['helder','half_bewolkt','bewolkt'])
    k['day_utc']=k.time.dt.strftime('%Y-%m-%d')
    return k


def prepare_data():
    solar,weather=load_influx_export()
    data=[]
    for label,g in solar.groupby('label',sort=True):
        try: pn=int(str(label).rsplit('-',1)[1])
        except (ValueError,IndexError): continue
        main=f'Pt100-{pn}'
        alternate=next((c for c in g.columns if c.startswith(('Pt100[df112]-','Pt100[1dd12]-')) and c.endswith(f'-{pn}')),None)
        keep=['_time','label','ff','impp','isc','vmpp','voc','CMP-10','Ref']+[x for x in [main,alternate] if x]
        x=g[keep].copy()
        for c in keep:
            if c not in ['_time','label']: x[c]=pd.to_numeric(x[c],errors='coerce')
        x['panel']=f'PV{pn}'
        x['T_main_C']=x[main] if main in x else np.nan
        x['T_alt_C']=x[alternate] if alternate else np.nan
        x['T_source']=np.select([x.T_main_C.notna(),x.T_alt_C.notna()],['hoofdkanaal','alternatief kanaal'],default='ontbreekt')
        # Only combine variants with the same panel suffix; retain the source and raw columns.
        x['T_panel_C']=x.T_main_C.combine_first(x.T_alt_C)
        data.append(x)
    p=pd.concat(data,ignore_index=True).sort_values(['_time','panel'])
    p['P_mpp_W']=p.impp*p.vmpp
    p['FF_calc_pct']=100*p.P_mpp_W/(p.voc*p.isc)
    p.loc[(p.voc<=0)|(p.isc<=0),'FF_calc_pct']=np.nan
    p['day_utc']=p._time.dt.strftime('%Y-%m-%d')
    w=weather.copy().sort_values('_time')
    w['T_air_raw_C']=pd.to_numeric(w['Temperature-PVMET500'],errors='coerce')
    # Do not interpolate an implausible ambient-temperature outlier; exclude it from analyses only.
    w['T_air_C']=w.T_air_raw_C.where(w.T_air_raw_C.between(-40,40))
    for c in ['Humidity-PVMET500','Pressure-PVMET500']: w[c]=pd.to_numeric(w[c],errors='coerce')
    w=w.drop_duplicates('_time')
    p=pd.merge_asof(p,w[['_time','T_air_raw_C','T_air_C','Humidity-PVMET500','Pressure-PVMET500']].sort_values('_time'),on='_time',direction='nearest',tolerance=pd.Timedelta('2min'))
    p['delta_T_C']=p.T_panel_C-p.T_air_C
    k=load_knmi()
    p['hour_end']=p._time.dt.ceil('h')
    # Hourly mean of solar records aligns to KNMI's hour-ending timestamp and preceding-hour Q integral.
    agg={c:'mean' for c in ['T_panel_C','T_air_C','delta_T_C','P_mpp_W','voc','ff','impp','vmpp','isc']}
    agg['CMP-10']='median'
    hourly=p.groupby(['panel','hour_end'],as_index=False).agg(agg)
    hourly=hourly.merge(k[['time','T_air_knmi_C','Q_J_cm2','G_knmi_Wm2','cloud_oktas','cloud_class','RH_pct','wind_ms','rain_mm','rain_flag']],left_on='hour_end',right_on='time',how='left')
    hourly['day_utc']=hourly.hour_end.dt.strftime('%Y-%m-%d')
    hourly['hour_sin']=np.sin(2*np.pi*hourly.hour_end.dt.hour/24)
    hourly['hour_cos']=np.cos(2*np.pi*hourly.hour_end.dt.hour/24)
    hourly['logG']=np.log(hourly.G_knmi_Wm2.clip(lower=1))
    hourly['logP']=np.log(hourly.P_mpp_W.clip(lower=1e-5))
    hourly['suspicious_T']=hourly.delta_T_C.notna() & ((hourly.delta_T_C < -15)|(hourly.delta_T_C>50))
    return p,w,k,hourly,solar


def duplicate_audit(solar):
    fields=['ff','impp','isc','vmpp','voc']; rows=[]
    for field in fields:
        piv=solar.pivot_table(index='_time',columns='label',values=field,aggfunc='first')
        for a,b in combinations(piv.columns,2):
            q=piv[[a,b]].dropna()
            if len(q):
                rows.append({'veld':field,'paneel_a':a.replace('PvDevice-','PV'),'paneel_b':b.replace('PvDevice-','PV'),'n_overlap':len(q),'exact_pct':100*np.isclose(q[a],q[b],rtol=0,atol=1e-12).mean(),'r':q[a].corr(q[b])})
    return pd.DataFrame(rows)


def panel_specific_analysis(hourly,n_boot=500,seed=41):
    """Estimate raw correlations and adjusted slopes separately for PV1–PV8.

    Models use each panel's own eligible rows, day fixed effects, and a day-block
    bootstrap. No panel is treated as a replicate of another panel. The shared
    weather exposure is retained as a dependence caveat, not counted as extra
    independent weather observations.
    """
    pairs=[('G_knmi_Wm2','P_mpp_W','r_G_Pmpp'),
           ('G_knmi_Wm2','delta_T_C','r_G_deltaT'),
           ('T_panel_C','voc','r_T_Voc'),('T_panel_C','isc','r_T_Isc'),
           ('T_panel_C','vmpp','r_T_Vmpp'),('T_panel_C','impp','r_T_Impp'),
           ('T_panel_C','ff','r_T_FF'),('T_panel_C','P_mpp_W','r_T_Pmpp')]
    corr_rows=[]; model_rows=[]

    def design(frame,terms,day_column):
        numeric=np.column_stack([np.ones(len(frame))]+[frame[c].to_numpy(float) for c in terms])
        days=pd.get_dummies(frame[day_column].astype(str),drop_first=True,dtype=float).to_numpy()
        return np.column_stack([numeric,days])

    def estimate(frame,outcome,terms,focus,model_name,model_seed):
        z=frame.dropna(subset=[outcome]+terms+['day_utc']).copy()
        if model_name=='logP': z=z[z.P_mpp_W.gt(0)].copy()
        days=np.array(sorted(z.day_utc.unique()))
        if len(z)<=len(terms)+1 or len(days)<2:
            return {'n':len(z),'days':len(days),'coef':np.nan,'ci_low':np.nan,'ci_high':np.nan}
        beta=np.linalg.lstsq(design(z,terms,'day_utc'),z[outcome].to_numpy(float),rcond=None)[0]
        index=1+terms.index(focus); rng=np.random.default_rng(model_seed)
        blocks={day:z[z.day_utc==day] for day in days}; boots=[]
        for _ in range(n_boot):
            parts=[]
            for j,day in enumerate(rng.choice(days,len(days),replace=True)):
                part=blocks[day].copy(); part['_boot_day']=f'b{j:03d}'; parts.append(part)
            sample=pd.concat(parts,ignore_index=True)
            value=np.linalg.lstsq(design(sample,terms,'_boot_day'),sample[outcome].to_numpy(float),rcond=None)[0][index]
            if np.isfinite(value): boots.append(float(value))
        lo,hi=np.quantile(boots,[.025,.975]) if boots else (np.nan,np.nan)
        return {'n':len(z),'days':len(days),'coef':float(beta[index]),'ci_low':float(lo),'ci_high':float(hi)}

    for panel,group in hourly.groupby('panel',sort=True):
        base=group[group.G_knmi_Wm2.gt(50)&group.delta_T_C.between(-15,50)&
                   group.wind_ms.notna()&group.T_air_C.notna()].copy()
        row={'panel':panel,'n_correlation':len(base),'days_correlation':int(base.day_utc.nunique())}
        for x,y,name in pairs:
            pair=base[[x,y]].dropna()
            row[name]=float(pair[x].corr(pair[y])) if len(pair)>2 else np.nan
            row['n_'+name]=len(pair)
        corr_rows.append(row)
        specs=[('deltaT','delta_T_C',['G_knmi_Wm2','wind_ms','T_air_C','hour_sin','hour_cos'],'G_knmi_Wm2'),
               ('Voc','voc',['T_panel_C','T_air_C','logG','wind_ms','hour_sin','hour_cos'],'T_panel_C'),
               ('logP','logP',['T_panel_C','T_air_C','logG','wind_ms','hour_sin','hour_cos'],'T_panel_C')]
        for name,outcome,terms,focus in specs:
            model=estimate(base,outcome,terms,focus,name,seed+int(panel[2:]))
            model_rows.append({'panel':panel,'model':name,**model})
    return pd.DataFrame(corr_rows),pd.DataFrame(model_rows)


def fit_day_bootstrap(data,formula,term,n_boot=500,seed=73):
    if smf is None:
        raise ImportError('statsmodels is required for the legacy pooled model; use panel_specific_analysis for the per-panel models.')
    fit=smf.ols(formula,data=data).fit(cov_type='cluster',cov_kwds={'groups':data.day_utc,'use_correction':True})
    days=np.array(sorted(data.day_utc.dropna().unique())); rng=np.random.default_rng(seed); vals=[]
    blocks={day:data[data.day_utc==day] for day in days}
    if len(days)<8:return fit,np.array([])
    for b in range(n_boot):
        chosen=rng.choice(days,len(days),replace=True); pieces=[]
        for j,day in enumerate(chosen):
            part=blocks[day].copy();part['_boot_day']=f'b{j:03d}';pieces.append(part)
        sample=pd.concat(pieces,ignore_index=True)
        f=formula.replace('C(day_utc)','C(_boot_day)')
        try:
            val=smf.ols(f,data=sample).fit().params.get(term,np.nan)
            if np.isfinite(val): vals.append(float(val))
        except Exception: pass
    return fit,np.asarray(vals)


def run_analysis(n_boot=500):
    """Run the primary per-panel analysis for PV1–PV8.

    Returns summary dictionaries, Plotly figures and prepared frames. Electrical
    duplication remains an explicit QA flag; it never merges physical panels.
    """
    p,w,k,h,solar=prepare_data()
    dup=duplicate_audit(solar)
    corr,models=panel_specific_analysis(h,n_boot=n_boot)
    weather_desc=weather_class_descriptives(h)
    weather_models=weather_class_models(h,n_boot=n_boot)
    ff=p.dropna(subset=['ff','FF_calc_pct']).copy(); ff['error_pp']=ff.ff-ff.FF_calc_pct
    tempcols=[c for c in solar.columns if str(c).startswith('Pt100')]
    summary={
        'solar_rows':len(solar),'weather_rows':len(w),
        'solar_time_start':str(solar._time.min()),'solar_time_end':str(solar._time.max()),
        'weather_time_start':str(w._time.min()),'weather_time_end':str(w._time.max()),
        'electrical_valid_by_panel':p.groupby('panel')[['ff','impp','isc','vmpp','voc','P_mpp_W']].count().to_dict(),
        'temp_channel_rows':{c:int(solar[c].notna().sum()) for c in tempcols},
        'ambient_above_40_count':int((w.T_air_raw_C>40).sum()),
        'ambient_invalid_humidity_count':int((~w['Humidity-PVMET500'].between(0,100)).sum()),
        'ff_qc':{'n':len(ff),'median_abs_error_pp':float(ff.error_pp.abs().median()),
                 'max_abs_error_pp':float(ff.error_pp.abs().max()),
                 'within_1pp_pct':float(100*(ff.error_pp.abs()<=1).mean())},
        'knmi_station':int(k.STN.mode().iloc[0]),'knmi_rows':len(k),
        'knmi_time_start':str(k.time.min()),'knmi_time_end':str(k.time.max()),
        'knmi_matched_hours':int(h.G_knmi_Wm2.notna().sum()),
        'panel_correlations':corr.to_dict('records'),
        'panel_models':models.to_dict('records'),
        'weather_class_descriptives':weather_desc.to_dict('records'),
        'weather_class_models':weather_models.to_dict('records'),
        'duplicate_pairs':dup.to_dict('records')
    }
    figs=make_figures(p,k,h,dup)
    frames={'raw':p,'weather':w,'knmi':k,'hourly':h,'duplicates':dup,'solar_export':solar}
    return summary,figs,frames

def model_summary(fit,boot,term):
    return {'coef':float(fit.params.get(term,np.nan)),'cluster_robust_p':float(fit.pvalues.get(term,np.nan)),'r_squared':float(fit.rsquared),'n':int(fit.nobs),'days':int(fit.model.data.frame.day_utc.nunique()),'day_bootstrap_95ci':[float(np.quantile(boot,.025)),float(np.quantile(boot,.975))] if len(boot) else None}


def make_figures(p,k,h,dup):
    figs={}
    t=p.dropna(subset=['T_panel_C']).copy()
    figs['temperature']=px.scatter(t,x='_time',y='T_panel_C',color='panel',symbol='T_source',hover_data=['T_air_C','delta_T_C'],title='Paneel- en omgevingstemperatuur',labels={'_time':'Tijd (UTC)','T_panel_C':'Paneeltemperatuur (°C)','panel':'Paneel','T_source':'Pt100-kanaal','T_air_C':'Omgeving (°C)','delta_T_C':'ΔT (°C)'})
    figs['weather_delta']=px.box(h[h.cloud_class.notna() & h.delta_T_C.notna()],x='cloud_class',y='delta_T_C',color='cloud_class',points='all',hover_data=['panel','hour_end','G_knmi_Wm2','wind_ms'],facet_col='panel',facet_col_wrap=4,title='Temperatuurverschil per KNMI-bewolkingsklasse en paneel',labels={'cloud_class':'Bewolking','delta_T_C':'ΔT: paneel − lokale lucht (°C)','G_knmi_Wm2':'Globale straling (W/m²)','wind_ms':'Wind (m/s)'})
    cmp=p.dropna(subset=['CMP-10']).groupby('_time',as_index=False)['CMP-10'].median().sort_values('_time')
    cmp=pd.merge_asof(cmp,k[['time','G_knmi_Wm2']].sort_values('time'),left_on='_time',right_on='time',direction='nearest',tolerance=pd.Timedelta('35min'))
    figs['cmp_knmi']=px.scatter(cmp,x='G_knmi_Wm2',y='CMP-10',hover_data=['_time'],title='CMP-10-exportwaarde versus KNMI-straling',labels={'G_knmi_Wm2':'KNMI uurgemiddelde globale straling (W/m²)','CMP-10':'CMP-10-exportwaarde (eenheid onbevestigd)'})
    power=h[h.P_mpp_W.gt(0)&h.G_knmi_Wm2.notna()].copy()
    figs['power_irradiance']=px.scatter(power,x='G_knmi_Wm2',y='P_mpp_W',color='T_panel_C',symbol='panel',hover_data=['hour_end','cloud_class','wind_ms'],facet_col='panel',facet_col_wrap=4,title='Berekend MPP-vermogen versus KNMI-straling per paneel',labels={'G_knmi_Wm2':'KNMI globale straling (W/m²)','P_mpp_W':'Pₘₚₚ (W)','T_panel_C':'Paneeltemperatuur (°C)','panel':'Paneel'})
    voc=h[h.voc.notna()&h.T_panel_C.notna()].copy()
    figs['voc_temp']=px.scatter(voc,x='T_panel_C',y='voc',color='G_knmi_Wm2',symbol='panel',hover_data=['hour_end','T_air_C','wind_ms'],facet_col='panel',facet_col_wrap=4,title='Openklemspanning versus paneeltemperatuur per paneel',labels={'T_panel_C':'Paneeltemperatuur (°C)','voc':'Voc (V)','G_knmi_Wm2':'KNMI straling (W/m²)','panel':'Paneel'})
    day=h[(h.G_knmi_Wm2.gt(50))&h.cloud_class.notna()].copy()
    figs['air_panel']=px.scatter(day.dropna(subset=['T_air_C','T_panel_C']),x='T_air_C',y='T_panel_C',color='panel',symbol='cloud_class',hover_data=['hour_end','G_knmi_Wm2','delta_T_C','wind_ms','P_mpp_W'],title='Paneeltemperatuur versus lokale buitenluchttemperatuur',labels={'T_air_C':'Buitenluchttemperatuur (°C)','T_panel_C':'Paneeltemperatuur (°C)','panel':'Paneel','cloud_class':'KNMI-bewolking'})
    figs['air_power']=px.scatter(day[day.P_mpp_W.gt(0)],x='T_air_C',y='P_mpp_W',color='panel',symbol='cloud_class',hover_data=['hour_end','T_panel_C','G_knmi_Wm2','wind_ms'],title='MPP-vermogen versus lokale buitenluchttemperatuur',labels={'T_air_C':'Buitenluchttemperatuur (°C)','P_mpp_W':'MPP-vermogen (W)','panel':'Paneel','cloud_class':'KNMI-bewolking'})
    figs['class_delta']=px.box(day.dropna(subset=['delta_T_C']),x='cloud_class',y='delta_T_C',color='cloud_class',facet_col='panel',facet_col_wrap=4,points='all',hover_data=['hour_end','G_knmi_Wm2','wind_ms'],title='Paneelopwarming naar KNMI-bewolkingsklasse',labels={'cloud_class':'Bewolking','delta_T_C':'ΔT (°C)'})
    figs['class_power']=px.box(day[day.P_mpp_W.gt(0)],x='cloud_class',y='P_mpp_W',color='cloud_class',facet_col='panel',facet_col_wrap=4,points='all',hover_data=['hour_end','G_knmi_Wm2','T_air_C','wind_ms'],title='MPP-vermogen naar KNMI-bewolkingsklasse',labels={'cloud_class':'Bewolking','P_mpp_W':'MPP-vermogen (W)'})
    d=dup[dup.veld=='impp']; panels=sorted(set(d.paneel_a)|set(d.paneel_b));z=np.full((len(panels),len(panels)),np.nan)
    for i,a in enumerate(panels):
        z[i,i]=100
        for j,b in enumerate(panels):
            if i==j:continue
            q=d[((d.paneel_a==a)&(d.paneel_b==b))|((d.paneel_a==b)&(d.paneel_b==a))]
            if len(q):z[i,j]=q.iloc[0].exact_pct
    figs['duplicates']=go.Figure(go.Heatmap(x=panels,y=panels,z=z,colorscale='Viridis',zmin=0,zmax=100,colorbar_title='Gelijke waarden (%)',hovertemplate='%{y} ↔ %{x}<br>%{z:.1f}% exact gelijk<extra></extra>'))
    figs['duplicates'].update_layout(title='Exacte gelijkheid van Impp per paneelpaar',xaxis_title='Paneel',yaxis_title='Paneel')
    for f in figs.values(): f.update_layout(template='plotly_white',hovermode='closest',legend_title_text='')
    return figs


def weather_class_descriptives(hourly):
    """Describe matched daytime measurements by KNMI cloud class and panel.

    Cloud classes are based on KNMI oktas (0–2 clear, 3–5 partly cloudy,
    6–8 overcast); code 9 is left unclassified. Only G>50 W/m² is included.
    """
    z=hourly[hourly.G_knmi_Wm2.gt(50)&hourly.cloud_class.notna()].copy()
    return (z.groupby(['panel','cloud_class'],observed=False)
        .agg(n_hours=('hour_end','nunique'),n_days=('day_utc','nunique'),
             n_Tair=('T_air_C','count'),n_Tpanel=('T_panel_C','count'),n_deltaT=('delta_T_C','count'),n_Pmpp=('P_mpp_W','count'),
             median_G_Wm2=('G_knmi_Wm2','median'),median_Tair_C=('T_air_C','median'),
             median_Tpanel_C=('T_panel_C','median'),median_deltaT_C=('delta_T_C','median'),
             median_Pmpp_W=('P_mpp_W','median'),median_wind_ms=('wind_ms','median'))
        .reset_index())


def weather_class_models(hourly,n_boot=500,seed=91):
    """Estimate per-panel cloud-class associations relative to overcast.

    The daytime models include local air temperature, KNMI wind, and time of
    day, but deliberately omit irradiance: cloud-associated irradiance is part
    of the total weather pathway being described. Whole UTC days are resampled.
    These observational contrasts are not causal effects.
    """
    levels=['bewolkt','half_bewolkt','helder']; rows=[]
    def matrix(z):
        cat=pd.Categorical(z.cloud_class,categories=levels)
        return np.column_stack([np.ones(len(z)),(cat=='half_bewolkt').astype(float),
            (cat=='helder').astype(float),z.T_air_C.to_numpy(float),z.wind_ms.to_numpy(float),
            z.hour_sin.to_numpy(float),z.hour_cos.to_numpy(float)])
    for panel,g in hourly.groupby('panel',sort=True):
        for outcome in ['delta_T_C','logP']:
            z=g[g.G_knmi_Wm2.gt(50)&g.cloud_class.notna()&g.T_air_C.notna()&g.wind_ms.notna()].copy()
            if outcome=='logP':
                z=z[z.P_mpp_W.gt(0)].copy(); z[outcome]=np.log(z.P_mpp_W)
            else:
                z=z.dropna(subset=[outcome])
            if len(z)<10 or z.day_utc.nunique()<3: continue
            beta=np.linalg.lstsq(matrix(z),z[outcome].to_numpy(float),rcond=None)[0]
            blocks={day:q for day,q in z.groupby('day_utc')}; days=np.array(sorted(blocks)); rng=np.random.default_rng(seed+int(panel[2:])+(100 if outcome=='logP' else 0))
            boot=[]
            for _ in range(n_boot):
                chosen=rng.choice(days,len(days),replace=True)
                sample=pd.concat([blocks[d] for d in chosen],ignore_index=True)
                b=np.linalg.lstsq(matrix(sample),sample[outcome].to_numpy(float),rcond=None)[0]
                boot.append(b[[1,2]])
            boot=np.asarray(boot)
            for index,label in [(1,'half_bewolkt_vs_bewolkt'),(2,'helder_vs_bewolkt')]:
                lo,hi=np.quantile(boot[:,index-1],[.025,.975]) if len(boot) else (np.nan,np.nan)
                rows.append({'panel':panel,'outcome':outcome,'contrast':label,'n':len(z),'days':int(z.day_utc.nunique()),
                    'days_overcast':int(z.loc[z.cloud_class.eq('bewolkt'),'day_utc'].nunique()),
                    'days_partly_cloudy':int(z.loc[z.cloud_class.eq('half_bewolkt'),'day_utc'].nunique()),
                    'days_clear':int(z.loc[z.cloud_class.eq('helder'),'day_utc'].nunique()),
                    'coef':float(beta[index]),'ci_low':float(lo),'ci_high':float(hi)})
    return pd.DataFrame(rows)
