# Invloed van weersomstandigheden op de temperatuur en elektrische prestaties van acht zonnepanelen


**Project:** Solar Field-dataanalyse · HvA Energielab / AMOLF  
**Locatie:** Science Park 104, Amsterdam  
**Dataperiode:** 23 oktober–17 november 2026  
**Rapport:** verkennende analyse · versie 1.2 · 18 november 2026

> Afgeleide resultaten zijn vrijgegeven voor projectvisualisatie. De ruwe SolarNL-export wordt niet als afzonderlijk bestand in dit rapport opgenomen.

## Samenvatting

Dit onderzoek onderzoekt hoe weer samenhangt met de temperatuur en elektrische prestaties van acht zonnepanelen. De primaire InfluxDB-export beslaat 23 oktober tot en met 17 november 2026. Voor aanvullende meteorologische context is KNMI-station 240 (Schiphol) gekoppeld aan de metingen. De koppeling levert globale straling, bewolking, wind, relatieve luchtvochtigheid en neerslag, maar meet niet op Science Park 104 en geeft geen instraling op het paneelvlak.

De lokale data bevatten 65.700 zonnepaneelrijen en 18.684 weerrijen. Van de elektrische metingen zijn 4.955 complete sets `Voc`, `Isc`, `Vmpp`, `Impp` en `FF` beschikbaar. De fill factor is intern consistent met `100 × Impp × Vmpp / (Isc × Voc)`: de mediane absolute afwijking is 0,0026 procentpunt en alle rijen liggen binnen 1 procentpunt. Eén PVMET500-luchttemperatuur boven 40 °C is als foutkandidaat behandeld en in berekeningen ontbrekend gelaten; de waarde is niet ingevuld.

De Pt100-kolommen zijn in twee niet-overlappende periodes geregistreerd. De twee tagfamilies overlappen niet, waardoor continuïteit en offset niet zijn vastgesteld. PV8 heeft sterke temperatuuranomalieën. Elektrische waarden van PV3–PV8 zijn bij veel tijdstippen vrijwel identiek; tussen PV4 en PV5 is `Impp` op alle 637 overlapmomenten exact gelijk. Daardoor is een rangorde van acht panelen niet verantwoord.

Alle acht panelen zijn afzonderlijk geanalyseerd. In de volledige KNMI-daglichtreeks was de mediane globale straling hoger bij helder dan bij bewolkt weer (253 tegenover 156 W/m²). In de kleine, gekoppelde paneelmetingen was de mediane `ΔT` onder helder weer voor alle acht labels hoger dan onder bewolkt weer; ook de ruwe MPP-medianen lagen hoger. De heldere vergelijking bevat echter slechts zes meetdagen. Modellen per paneel met correctie voor lokale buitenluchttemperatuur, wind en uur geven brede onzekerheidsintervallen: alle intervallen voor helder–bewolkt `ΔT` omvatten nul, evenals die voor vermogen bij PV3–PV8. De data ondersteunen dus de verwachte richting, maar bepalen de grootte van het weertype-effect niet betrouwbaar. Los daarvan zijn Voc-temperatuurhellingen negatief maar onzeker en zijn de temperatuurhellingen voor `ln(Pmpp)` onverwacht positief; dit is geen bewijs dat warmte het vermogen verhoogt.

**Antwoord:** de beschikbare metingen suggereren dat meer globale straling samenhangt met een groter temperatuurverschil tussen paneel en omgevingslucht. Met deze korte, onvolledig gekalibreerde meetreeks kan niet betrouwbaar worden vastgesteld welk causaal effect paneeltemperatuur heeft op Voc of MPP-vermogen. Sensor- en kanaalvalidatie, onafhankelijke instraling op paneelvlak, paneelspecificaties en langere meetreeksen zijn nodig voor een definitieve conclusie. De modules zijn wel afzonderlijk gemodelleerd, maar niet onderling gerangschikt.

## Inhoudsopgave

- [Samenvatting](#samenvatting)
- [Afkortingen en symbolen](#afkortingen-en-symbolen)
1. [Inleiding](#1-inleiding)  
2. [Theoretisch kader](#2-theoretisch-kader)  
3. [Hypothesen](#3-hypothesen)  
4. [Data en methode](#4-data-en-methode)  
5. [Resultaten](#5-resultaten)  
6. [Discussie](#6-discussie)  
7. [Conclusie](#7-conclusie)  
8. [Aanbevelingen](#8-aanbevelingen)  
9. [Bronnen](#9-bronnen)

## Afkortingen en symbolen

| Symbool/afkorting | Betekenis | Eenheid |
|---|---|---|
| `G` | Globale horizontale straling uit KNMI | W m⁻² |
| `G_POA` | Instraling in het vlak van de module (plane of array) | W m⁻² |
| `T_a` | Buitenluchttemperatuur | °C |
| `T_m` / `T_paneel` | Gemeten module- of paneeltemperatuur; sensorlocatie niet bevestigd | °C |
| `ΔT` | Paneeltemperatuur minus buitenluchttemperatuur | °C |
| `V_oc` | Openklemspanning | V |
| `I_sc` | Kortsluitstroom | A |
| `V_mpp`, `I_mpp` | Spanning en stroom bij maximum power point | V, A |
| `P_mpp` | Vermogen bij maximum power point | W |
| `FF` | Fill factor | % |
| `BI` | Betrouwbaarheidsinterval (bootstrapinterval in dit rapport) | — |
| `UTC` | Coordinated Universal Time | — |
| `PV` | Photovoltaic; label voor een afzonderlijk paneel | — |


## 1. Inleiding

### 1.1 Aanleiding

Een zonnepaneel wordt buiten niet onder één vaste toestand gebruikt. De instraling verandert door zonnestand en bewolking; de buitenlucht, wind en neerslag veranderen eveneens. Die invloeden werken gelijktijdig op het paneel. Meer zonlicht kan de fotostroom en daarmee het elektrisch vermogen verhogen, maar het geabsorbeerde deel van de straling warmt ook de module op. Tegelijk voert wind warmte af en beïnvloedt de buitenluchttemperatuur het thermische evenwicht. Een waargenomen stijging van vermogen bij een hogere paneeltemperatuur betekent daarom niet automatisch dat warmte het vermogen verhoogt: beide kunnen door dezelfde toename in instraling worden veroorzaakt.

Dit onderzoek is uitgevoerd met meetreeksen van acht modules in het Solar Field van het HvA Energielab en AMOLF. De vraag is praktisch relevant voor het interpreteren van buitenmetingen: wanneer verandert het vermogen door de beschikbare lichtintensiteit, wanneer verandert het door de temperatuurrespons, en wanneer kan een afwijking worden verklaard door de meetketen? Die vragen zijn alleen zinvol te beantwoorden wanneer eerst de kwaliteit en onafhankelijkheid van de meetkanalen worden onderzocht.

### 1.2 Wetenschappelijke en praktische relevantie

Temperatuur is een belangrijke bedrijfsvariabele van fotovoltaïsche modules. Bij veel kristallijne-siliciumtechnologieën neemt de openklemspanning toe wanneer de celtemperatuur daalt, terwijl het vermogen bij vaste instraling doorgaans afneemt naarmate de cel warmer wordt [3]. In veldmetingen is de instraling echter zelden constant. Bewolking verlaagt doorgaans de directe component van zonnestraling, maar verandert ook de diffuse component; wind en luchttemperatuur veranderen tegelijk. Een analyse die alleen paneeltemperatuur en vermogen tegenover elkaar zet, kan deze mechanismen niet onderscheiden.

Voor het Energielab en AMOLF is het daarom van belang om niet alleen samenhang te rapporteren, maar ook aan te geven welke samenhang meetkundig te vertrouwen is. Dit rapport maakt zichtbaar welke conclusies rechtstreeks uit de meetdata volgen, welke slechts passen bij een fysische verwachting en welke aanvullende instrumentatie nodig is om een effect causaal of paneelspecifiek te toetsen.

### 1.3 Onderzoeksdoel

Het doel is de beschikbare veldmetingen van acht zonnepanelen systematisch te controleren en vervolgens per paneel te onderzoeken hoe meteorologische omstandigheden samenhangen met (1) de paneeltemperatuur ten opzichte van de buitenlucht en (2) elektrische grootheden zoals `Voc`, `Isc`, `Vmpp`, `Impp`, fill factor en MPP-vermogen. De analyse moet de totale associatie met weertype onderscheiden van de temperatuurassociatie bij statistische correctie voor gemeten verstorende variabelen. De uitkomsten worden met onzekerheidsmarges en expliciete meetbeperkingen gerapporteerd.

### 1.4 Onderzoeksvraag

*Hoe hangen weersomstandigheden samen met (I) de paneeltemperatuur en (II) de elektrische prestaties van elk van de acht zonnepanelen, en in hoeverre kan in deze meetreeks een zelfstandige associatie tussen paneeltemperatuur en elektrische prestaties worden onderscheiden van instraling en andere weerfactoren?*

### 1.5 Deelvragen

1. Welke thermische, meteorologische en elektrische meetkanalen zijn beschikbaar, en welke kwaliteitsproblemen begrenzen de analyse?
2. **Deel I — weer en paneeltemperatuur:** hoe hangen globale straling, bewolkingsklasse, wind en lokale buitenluchttemperatuur samen met de paneeltemperatuur en met `ΔT = T_paneel − T_lucht`?
3. **Deel II — paneeltemperatuur en elektrische prestaties:** welke associaties bestaan tussen paneeltemperatuur en `Voc`, `Isc`, `Vmpp`, `Impp`, fill factor en `P_mpp` wanneer gemeten instraling, buitenluchttemperatuur, wind en tijd worden meegewogen?
4. In hoeverre zijn deze patronen per paneel interpreteerbaar, gegeven temperatuuranomalieën en mogelijke duplicatie van elektrische meetkanalen?
5. Welke conclusies kunnen met de meetdekking en onzekerheid worden getrokken, en welke blijven onbeslist?

### 1.6 Afbakening

De primaire export beslaat 23 oktober tot en met 17 november 2026. Dat korte meetvenster is geschikt voor een verkennende analyse van samenhang binnen deze periode, maar niet voor uitspraken over seizoenen, jaaropbrengst, degradatie of representatieve langetermijnprestaties. De aanvullende KNMI-gegevens komen van station 240 (Schiphol), niet van Science Park 104. De KNMI-straling is globale horizontale straling en geen instraling in het paneelvlak. De lokale CMP-10-reeks wordt vanwege de niet-gevalideerde schaal/offset niet als absolute irradiantie gebruikt.

De acht fysieke modules worden afzonderlijk geanalyseerd. Dat betekent niet dat de acht elektrische reeksen aantoonbaar onafhankelijk zijn: mogelijke kanaalduplicatie wordt als beperking meegenomen. Het rapport rangschikt de panelen daarom niet en vergelijkt geen rendementen zonder paneelspecificaties, oppervlak en gevalideerde kanalen.

### 1.7 Leeswijzer

Hoofdstuk 2 beschrijft de thermische en elektrische principes achter de verwachte relaties. Hoofdstuk 3 vertaalt deze principes naar toetsbare hypothesen. Hoofdstuk 4 documenteert bronnen, kwaliteitscontroles, koppeling, regressies en onzekerheidsbepaling. Hoofdstuk 5 presenteert eerst de datakwaliteit en splitst de resultaten daarna in twee delen: Deel I behandelt weer en thermische respons; Deel II behandelt de elektrische respons en de vraag of een afzonderlijk temperatuureffect zichtbaar is. Hoofdstuk 6 bespreekt de betekenis en beperkingen; hoofdstuk 7 beantwoordt de onderzoeksvraag. Hoofdstuk 8 bevat aanbevelingen voor validatie en vervolgmetingen. De interactieve versies van de grafieken zijn beschikbaar op de SolarNL-projectwebsite; de notebook bevat de reproduceerbare berekeningen.

## 2. Theoretisch kader

Dit hoofdstuk beschrijft de natuurkundige relaties die nodig zijn om de meetresultaten te interpreteren. De vergelijkingen geven verwachtingen onder expliciete randvoorwaarden. Ze zijn geen parameters die zonder specificaties of kalibratie rechtstreeks op de modules in het Solar Field kunnen worden toegepast.

### 2.1 Thermische respons van een PV-module

Een PV-module absorbeert een deel van de invallende zonnestraling. De geabsorbeerde energie wordt verdeeld over elektrische omzetting, convectie naar de lucht, langgolvige warmtestraling en warmtegeleiding naar de draagconstructie. Hogere instraling verhoogt doorgaans de warmtetoevoer. Wind kan door convectie warmte afvoeren. De omgevingstemperatuur bepaalt mede het thermische startniveau.

Het empirische Faiman-model beschrijft de stationaire moduletemperatuur als [1,2,7]:

`T_m = T_a + G_POA / (U_0 + U_1 v_w)`  (1)

Hierin is `T_m` de moduletemperatuur (°C), `T_a` de luchttemperatuur (°C), `G_POA` de instraling op het modulevlak (W m⁻²), `v_w` de windsnelheid (m s⁻¹) en zijn `U_0` en `U_1` empirische warmteverliescoëfficiënten. Deze coëfficiënten hangen af van moduleconstructie en montage [1,2]. De vergelijking veronderstelt een quasi-stationaire toestand en beschrijft thermische traagheid, schaduw en lokale temperatuurgradiënten niet expliciet.

Voor deze analyse is de KNMI-straling van station 240 (Schiphol) geen `G_POA`: dit is regionale globale horizontale straling. De Faiman-relatie onderbouwt daarom alleen de verwachte richting van verbanden. De coëfficiënten zijn niet gefit. Ook is de fysieke plaatsing van de Pt100-sensoren niet bevestigd; een achterzijde-temperatuur is niet noodzakelijk gelijk aan de celtemperatuur.

### 2.2 Elektrische respons van een PV-module

De stroom-spanningscurve van een PV-module wordt vaak benaderd met het één-diode-equivalent model [3]:

`I = I_ph − I_0 [exp(q(V + I R_s)/(n N_s k_B T_c)) − 1] − (V + I R_s)/R_sh`  (2)

Hierin is `I_ph` de fotostroom, `I_0` de diode-verzadigingsstroom, `V` de spanning, `R_s` en `R_sh` de serie- en shuntweerstand, `n` de idealiteitsfactor, `N_s` het aantal seriegeschakelde cellen, `q` de elementaire lading, `k_B` de constante van Boltzmann en `T_c` de celtemperatuur in kelvin. Het model wordt in dit onderzoek niet op de data gefit. Het maakt wel duidelijk dat instraling en temperatuur verschillende onderdelen van de I–V-respons beïnvloeden: meer instraling verhoogt voornamelijk de fotostroom; temperatuur beïnvloedt onder meer de verzadigingsstroom en daarmee de spanning.

De openklemspanning `V_oc` wordt gemeten bij `I = 0`; de kortsluitstroom `I_sc` bij `V = 0`. Het maximum power point (MPP) is het punt op de I–V-curve waar het product van stroom en spanning maximaal is:

`P_mpp = V_mpp I_mpp`  (3)

De fill factor is gedefinieerd als:

`FF = 100 × P_mpp / (V_oc I_sc)`  (4)

De factor 100 geeft FF als percentage. De interne controle op de geëxporteerde FF valideert de rekenkundige consistentie van de export, niet de kalibratie van de onderliggende stroom- en spanningskanalen.

Rond een referentietoestand kan temperatuurafhankelijkheid bij constante instraling lokaal worden benaderd met [3]:

`V_oc(T_c) ≈ V_oc,ref + β_Voc (T_c − T_ref)`  (5a)  
`P_mpp(T_c) ≈ P_mpp,ref [1 + γ_P (T_c − T_ref)]`  (5b)

Voor veel kristallijn-siliciummodules zijn `β_Voc` en `γ_P` negatief; exacte waarden zijn modulespecifiek en horen uit fabrikantgegevens te komen [3]. Deze lineaire benadering geldt niet onafhankelijk van instraling of meetcondities. Omdat moduletechnologie, fabrikantcoëfficiënten en een gekalibreerde celtemperatuur ontbreken, worden de coëfficiënten in deze studie niet als bekende waarden verondersteld. IEC 60891 beschrijft correcties van gemeten I–V-karakteristieken, maar toepassing vraagt meer informatie dan de huidige export bevat [4].


## 3. Hypothesen

De hypothesen zijn afgeleid uit de thermische energiebalans en de temperatuur- en instralingsafhankelijkheid van de I–V-curve. Het zijn vooraf geformuleerde verwachtingen, geen aannames dat de meetdata ze noodzakelijk bevestigen. De richting geldt alleen onder vergelijkbare omstandigheden voor de overige relevante variabelen. De tabel beschrijft de verwachte associatie; door het observationele ontwerp is een gevonden verband op zichzelf geen bewijs voor causaliteit.

| Variabelen | Verwachte richting | Hypothese |
|---|---|---|
| `G` en `ΔT = T_paneel − T_lucht` | Positief bij vergelijkbare wind, lucht en montage | H1: `β_G > 0` |
| Wind en `ΔT` | Negatief door sterkere convectieve koeling | Controlevariabele; verwachte `β_wind < 0` |
| `G` en `I_sc`, `I_mpp` of `P_mpp` | Overwegend positief, door grotere fotostroom | Instralingsrespons; niet het temperatuur-effect |
| `T_c` en `V_oc`/`P_mpp` | Voor veel silicium-PV negatief bij constante `G` | H2/H3: `β_T < 0`, indien technologie en metingen vergelijkbaar zijn |
| Heldere versus bewolkte lucht en `ΔT` | Helder weer geeft doorgaans grotere `G` en dus grotere `ΔT`, bij vergelijkbare lucht en wind | H4: heldere uren hebben grotere mediane `ΔT` dan bewolkte uren |
| Heldere versus bewolkte lucht en `P_mpp` | Helder weer verhoogt doorgaans fotostroom en MPP-vermogen | H5: MPP-vermogen is hoger tijdens heldere uren; dit is een totaal weereffect, niet een warmte-effect |

Een ruwe temperatuur-vermogenscorrelatie vermengt de directe invloed van instraling met de thermische respons: zon kan zowel vermogen als temperatuur verhogen. H2 en H3 kunnen daarom alleen worden onderzocht met correctie voor gemeten verstorende variabelen. Zelfs na correctie blijft de analyse observationeel en bewijst zij geen causaliteit.

Voor weertype geldt een aanvullende verwachting. KNMI-bewolking wordt gecodeerd in achtsten: 0–2 okta wordt hier als helder, 3–5 als halfbewolkt en 6–8 als bewolkt beschouwd; code 9 is onbekend en uitgesloten [5,8]. Bij heldere lucht verwachten we doorgaans meer globale straling en daardoor grotere paneelopwarming boven de lucht (`ΔT`) en meer elektrische productie. Dit is een verwachting over het totale weereffect: instraling is een tussenliggend mechanisme van bewolking naar paneelrespons en wordt daarom niet als covariaat opgenomen in de weertypevergelijking. Bewolking is geen exacte proxy voor instraling op het paneelvlak; gebroken wolken, zonshoek, diffuse straling en regionale afstand kunnen de relatie veranderen.


Voor de inferentie is de nulhypothese per model dat de conditionele coëfficiënt voor het betreffende effect gelijk is aan nul. Een interval dat nul omvat, wordt geïnterpreteerd als onvoldoende precisie om de richting met deze dataset vast te stellen; het bewijst niet dat er geen fysisch effect bestaat. Omdat de studie observationeel is en slechts weinig onafhankelijke meetdagen bevat, worden de hypothesen verkennend getoetst en niet als causale experimenten geïnterpreteerd.


## 4. Data en methode

### 4.1 Primaire meetdata

De bron is een InfluxDB-export met acht panel labels (`PvDevice-1` tot en met `PvDevice-8`) en een PVMET500-weerreeks. De solar export bevat 65.700 rijen van 23 oktober 2026 13:46 UTC tot 17 november 2026 16:30 UTC. De weerreeks bevat 18.684 rijen van 23 oktober 13:46 UTC tot 17 november 16:31 UTC.

Per paneel zijn de beschikbare complete elektrische sets: PV1 696, PV2 706, PV3 638, PV4 637, PV5 637, PV6 637, PV7 502 en PV8 502. Dit zijn meetmomenten, geen onafhankelijke replicaten.

### 4.2 Aanvullende meteorologie

KNMI-station 240, Schiphol Airport, is gekozen als dichtstbijzijnde goed gedocumenteerde bron met uurgegevens voor temperatuur, globale straling, bewolking, relatieve vochtigheid, wind en neerslag. De verkregen serie bevat 600 uurwaarnemingen van 23 oktober 01:00 tot 17 november 00:00 UTC. KNMI-uurtijdstempels geven het einde van het voorafgaande uurvak. De solar-metingen zijn per paneel geaggregeerd naar hetzelfde uurvak en op eindtijd gekoppeld. De KNMI-reeks stopt eerder dan de laatste solar-metingen.

KNMI rapporteert `Q` in J/cm² per uurvak [5]. De omzetting naar een gemiddeld vermogen is `Q × 10 000 / 3 600` W/m². Wind in tienden m/s is gedeeld door 10; temperatuur in tienden °C door 10. Bewolking is ingedeeld in helder (0–2 okta), halfbewolkt (3–5) en bewolkt (6–8); code 9 en ontbrekende waarden blijven onbekend. Positieve neerslagsommen zijn als nat uur gemarkeerd. De weercode `WW` ontbreekt in deze export, dus de classificatie gebruikt bewolking en neerslagindicatoren.

Schiphol is regionale context en ligt buiten de meetlocatie. De data zijn niet gebruikt als vervanging voor lokale plane-of-array-instraling. KNMI vermeldt bovendien dat uurlijkse langjarige reeksen door stationsverplaatsingen en methodewijzigingen niet geschikt zijn voor trendanalyse.

### 4.3 Opschoning en synchronisatie

De Influx-export is per tabel gesplitst en numeriek getypeerd. Dubbele combinaties van tijdstempel en paneellabel zijn gecontroleerd. PVMET500-luchtvochtigheid viel in de geaccepteerde 0–100%-range. Eén luchttemperatuurwaarde boven 40 °C is als foutkandidaat gemarkeerd; deze blijft in de ruwe kolom staan en wordt in analysekolommen ontbrekend gemaakt. Er is niet geïnterpoleerd.

Pt100-metingen zijn op basis van het paneelsuffix gekoppeld aan het overeenkomstige label. De hoofdtag (`Pt100-n`) en alternatieve tag (met exportprefix `df112` of `1dd12`) zijn in niet-overlappende periodes geregistreerd. Er zijn geen gelijktijdige paren om hun offset te controleren. De reeks is daarom alleen als gecombineerde kandidaatreeks gebruikt met behoud van tagherkomst; de sensor-paneel-mapping moet worden bevestigd.

### 4.4 Correlatie, regressiemodellen en onzekerheid

De ruwe lineaire samenhang is samengevat met Pearson-correlatie:

`r_xy = cov(x,y)/(s_x s_y)`  (6)

`cov(x,y)` is de steekproefcovariantie en `s_x`, `s_y` zijn standaardafwijkingen. `r` loopt van −1 tot +1, is dimensieloos en corrigeert niet voor andere variabelen. Daarom zijn daarnaast multivariabele lineaire modellen gebruikt.

Voor de temperatuurrespons is het model:

`ΔT_(d,h) = β_0,i + β_G,i G_(d,h) + β_W,i W_(d,h) + β_a,i T_a,(d,h) + f_i(h) + δ_(d,i) + ε_(i,d,h)`  (7)

Voor de elektrische respons zijn afzonderlijke modellen geschat:

`V_oc,i,d,h = α_0,i + α_T,i T_paneel + α_a,i T_a + α_G,i ln(G) + α_W,i W + f_i(h) + δ_(d,i) + ε_(i,d,h)`  (8a)

`ln(P_mpp,i,d,h) = θ_0,i + θ_T,i T_paneel + θ_a,i T_a + θ_G,i ln(G) + θ_W,i W + f_i(h) + κ_(d,i) + ε_(i,d,h)`  (8b)

De temperatuurcoëfficiënt is per paneel respectievelijk `α_T,i` of `θ_T,i`. `i` duidt de afzonderlijk gemodelleerde module aan, `d` de kalenderdag en `h` het uur. `f_i(h)` is een paneelspecifieke dagcyclus met sinus- en cosinus-termen. In deze specificatie is geen paneelintercept nodig, omdat ieder paneel een eigen regressie krijgt. De modellen schatten conditionele associaties onder de gekozen specificatie, niet experimentele causale effecten.

Alle acht panelen zijn afzonderlijk voor de hoofdmodellen gebruikt. Per paneel is een eigen regressie geschat op de eigen uurregels; er is dus geen gemiddelde paneelcoëfficiënt berekend. Dit sluit aan bij de fysieke verschillen tussen modules. Elektrische kanaalduplicatie blijft een meetkwaliteitsrisico en beperkt de interpretatie van paneelspecifieke elektrische resultaten, maar is geen grond om de fysieke modules samen te voegen. De ruwe correlaties gebruiken daglichturen met `G > 50 W/m²` en geldige waarden voor het betreffende variabelenpaar; n verschilt daarom ook per elektrisch variabelenpaar (80 voor PV1–PV2, 77 voor PV3–PV6, 53 voor PV7 en 46 voor PV8). Modellen gebruiken hun eigen complete-case subset: ΔT-model n=80 voor PV1–PV7 en 51 voor PV8; Voc- en vermogensmodellen n=80/77 voor PV1–PV6, 53 voor PV7 en 46 voor PV8. Dit verschil ontstaat doordat elektrische waarden ontbreken; de modellen delen dus niet noodzakelijk dezelfde rijen.

De onzekerheidsintervallen zijn berekend met 500 bootstrap-herhalingen waarin volledige dagen met teruglegging zijn getrokken. De modellen bevatten 8–14 dagclusters per paneel; dat is weinig voor sterke inferentie. De intervallen zijn dagblok-bootstrapintervallen. Er worden geen cluster-p-waarden als beslissend bewijs gebruikt; resultaten zijn daarom verkennend.

Instrumentele Type-B meetonzekerheid is niet numeriek berekend doordat datasheets, kalibratiecertificaten, resoluties en montagegegevens ontbreken. Voor `P = IV` geldt eerste-orde onzekerheidspropagatie [6]:

`u²(P) ≈ I²u²(V) + V²u²(I) + 2IV·cov(I,V)`

De covariantie tussen stroom en spanning is niet bekend. De bootstrapintervallen beschrijven dus regressievariatie over tijdsblokken, niet de volledige metrologische meetonzekerheid.

## 5. Resultaten

De resultaten beantwoorden de deelvragen in twee stappen. **Deel I** beschrijft hoe het weer samenhangt met de thermische toestand van de modules. **Deel II** onderzoekt de elektrische verbanden en maakt expliciet waarom ruwe temperatuur-vermogenscorrelaties niet als temperatuureffect mogen worden gelezen.

### 5.1 Datakwaliteit

| Controle | Uitkomst | Betekenis |
|---|---:|---|
| Complete elektrische sets | 4.955 | Verdeeld over acht labels; niet gelijk aan onafhankelijke modules |
| Omgevingstemperatuur >40 °C | 1 waarde | Voor analyse als ontbrekend behandeld, niet gecorrigeerd |
| PVMET500-luchtvochtigheid buiten 0–100% | 0 van 18.684 | Geen ongeldige waarden volgens deze grens |
| Mediane absolute FF-afwijking t.o.v. berekening | 0,0026 procentpunt | Interne formuleconsistentie is hoog |
| Maximum absolute FF-afwijking | 0,0243 procentpunt | Alle FF-waarden binnen 1 procentpunt |
| Pt100-tags | 2 tagfamilies | Geen overlap; tagoffset niet toetsbaar |

PV8 heeft waarden die een fysieke controle vereisen: de hoofdtag loopt op tot ongeveer 85 °C en de alternatieve tag varieert tot onder −10 °C en boven 95 °C. Er zijn ook waarden die sterk van de lokale lucht afwijken. Zonder montage- en kalibratiegegevens is niet vast te stellen of dit sensorplaatsing, kanaaltoewijzing, bedrading of een exportfout betreft. Deze reeks is geen basis voor een paneelrangschikking.

De elektrische metingen wijzen op mogelijke gedeelde of gekloonde kanalen. `Impp` van PV4 en PV5 is exact gelijk op 637 overlappende tijdstippen. Veel vergelijkingen binnen PV3–PV8 hebben exact gelijke waarden op ongeveer 97–100% van overlapmomenten. Dit patroon is te sterk om panelen als acht onafhankelijke elektrische meetkanalen te behandelen, maar bewijst op zichzelf niet waar in de meetketen de duplicatie ontstaat. PV1 en PV2 zijn niet exact gelijk; hun Impp-correlatie is wel 0,997, wat gemeenschappelijke weersinvloeden én mogelijke gedeelde meetstructuur kan weerspiegelen.

### 5.2 Deel I — Weer en paneeltemperatuur

**Kernresultaat.** In de volledige KNMI-daglichtreeks was de mediane globale straling hoger tijdens heldere dan tijdens bewolkte uren: 253 tegenover 156 W/m². In de veel kleinere gekoppelde paneelreeks was de mediane `ΔT` tijdens heldere uren hoger voor alle acht labels. De absolute paneeltemperatuur was niet voor elk label hoger; de lokale lucht was tijdens de heldere uren in deze subset juist koeler (mediaan 13,6 °C tegenover 14,5 °C). Slechts zes heldere meetdagen zijn gekoppeld. De gecorrigeerde intervallen voor het heldere–bewolkte verschil in `ΔT` omvatten nul voor alle panelen. De richting is dus suggestief, maar het weertype-effect is met deze dataset niet precies vastgesteld.

#### 5.2.1 Straling en temperatuurverschil boven de buitenlucht

KNMI-station 240 leverde regionale uurcontext; dit station is niet op Science Park 104 en de globale straling is horizontaal, niet in het paneelvlak. De lokale CMP-10-export is niet bruikbaar als absolute straling zonder kalibratie: waarden liggen ook bij KNMI-nachtstraling boven nul. De vergelijking met KNMI is daarom diagnostisch en levert geen absolute instralingscorrectie.

Voor elk paneel is een apart model geschat voor `ΔT = T_paneel − T_lucht`. De regressiehellingen voor KNMI-straling waren positief voor PV1–PV8. De puntschattingen lopen uiteen van 0,0266 tot 0,0996 °C per W/m². De dagblok-bootstrapintervallen liggen voor alle acht boven nul; de onzekerheid is vooral groot bij PV8, waar minder dagen bruikbaar zijn (11 tegenover 14 bij PV1–PV7). Dit ondersteunt binnen de gebruikte data een positieve conditionele associatie, geen lokaal of causaal effect van paneelvlak-instraling.

#### 5.2.2 Buitenlucht en paneeltemperatuur

De relatie is per paneel bekeken op gematchte daglichturen (`G > 50 W/m²`). De onderstaande Pearson-correlaties zijn ruwe verbanden. Een correlatie van `T_lucht` met `P_mpp` is geen maat voor het temperatuurcoëfficiënt: instraling verschilt tussen uren en bepaalt de stroom sterk.

| Paneel | n (T_lucht–T_paneel) | r(T_lucht,T_paneel) | n (T_lucht–P_mpp) | r(T_lucht,P_mpp) |
|---|---:|---:|---:|---:|
| PV1 | 80 | +0,627 | 80 | +0,070 |
| PV2 | 80 | +0,069 | 80 | +0,064 |
| PV3 | 80 | +0,512 | 77 | −0,163 |
| PV4 | 80 | +0,444 | 77 | −0,163 |
| PV5 | 80 | +0,561 | 77 | −0,163 |
| PV6 | 80 | +0,481 | 77 | −0,166 |
| PV7 | 80 | +0,280 | 53 | +0,064 |
| PV8 | 80 | −0,158 | 46 | +0,064 |

De meeste panelen tonen een positieve samenhang tussen buitenlucht- en paneeltemperatuur, maar die is zwak voor PV2 en negatief voor PV8. Dit is geen vanzelfsprekend thermisch resultaat en onderstreept de behoefte aan bevestiging van Pt100-mapping en montage. De correlatie tussen buitenluchttemperatuur en vermogen ligt per paneel dicht bij nul of is licht negatief. Dat is logisch mogelijk: buitenlucht alleen bepaalt de elektrische productie niet; bewolking en instraling variëren tegelijk. De interactieve spreidingsdiagrammen tonen daarom ook paneel, bewolkingsklasse, wind, instraling en tijdstip.

#### 5.2.3 Helder, halfbewolkt en bewolkt weer

De KNMI-classificatie is gekoppeld aan de uurregels. In de volledige KNMI-reeks met `G > 50 W/m²` zijn er 37 heldere uren over 10 dagen, 16 halfbewolkte uren over 10 dagen en 115 bewolkte uren over 23 dagen. De mediane globale straling is respectievelijk 253, 207 en 156 W/m². Dat volgt de vooraf verwachte richting: de heldere categorie heeft de hoogste mediane straling. De categorieën bevatten echter sterk ongelijke aantallen waarnemingen.

Voor de gekoppelde temperatuurgrafiek blijven 11 heldere, 10 halfbewolkte en 59 bewolkte uurwaarden per paneel over (respectievelijk 6, 6 en 13 meetdagen). De elektrische waarden zijn vaker ontbrekend bij PV3–PV8. In deze kleine gekoppelde subset is de mediane KNMI-straling 156, 207 en 142 W/m². De heldere subset is dus niet representatief voor alle heldere KNMI-uren; de steekproefvolgorde is niet langer monotone. Dit is een belangrijke beperking bij de interpretatie van de categorieplot.

| Paneel | n ΔT (helder / half / bewolkt) | Mediaan ΔT helder / bewolkt (°C) | Mediaan Pmpp helder / bewolkt (W) |
|---|---:|---:|---:|
| PV1 | 11 / 10 / 59 | −0,61 / −2,05 | 143,0 / 63,5 |
| PV2 | 11 / 10 / 59 | 10,69 / 7,48 | 150,4 / 63,5 |
| PV3 | 11 / 10 / 59 | 4,00 / 2,89 | 123,5 / 47,0 |
| PV4 | 11 / 10 / 59 | 3,19 / 0,59 | 123,5 / 47,0 |
| PV5 | 11 / 10 / 59 | −1,15 / −1,47 | 123,5 / 47,0 |
| PV6 | 11 / 10 / 59 | 0,04 / −1,16 | 123,5 / 47,0 |
| PV7 | 11 / 10 / 59 | −0,02 / −1,40 | 123,5 / 60,1 |
| PV8 | 11 / 10 / 59 | 8,66 / −0,54 | 123,5 / 60,1 |

Voor `ΔT` zijn per module 11 heldere, 10 halfbewolkte en 59 bewolkte uren beschikbaar. Voor `P_mpp` zijn er door ontbrekende elektrische metingen 11/10/59 geldige uren bij PV1–PV2, 9/10/58 bij PV3–PV6 en 9/8/36 bij PV7–PV8. In de gekoppelde metingen is de mediane lokale buitenluchttemperatuur tijdens helder weer 13,6 °C en tijdens bewolkt weer 14,5 °C. De absolute paneeltemperatuur is daardoor niet bij alle panelen hoger onder heldere lucht; de buitenlucht was in deze subset juist koeler. Het temperatuurverschil `ΔT` is groter tijdens heldere dan bewolkte uren voor alle acht labels, maar het verschil is bij PV8 waarschijnlijk vertekend door de al vastgestelde temperatuuranomalieën. Dit illustreert waarom `T_paneel` en `ΔT` apart moeten worden bekeken.

Als aanvullende analyse is per paneel een model geschat voor het verschil tussen helder en bewolkt weer, met controle voor lokale luchttemperatuur, wind en uur van de dag. `G` is bewust weggelaten zodat de totale relatie van bewolking via instraling behouden blijft. Voor het vermogen is de uitkomst `ln(P_mpp)` omgerekend naar procentueel verschil. Intervallen komen uit 500 dagblok-bootstrapsteekproeven.

| Paneel | Helder–bewolkt ΔT (°C, 95%-BI) | Helder–bewolkt Pmpp (%) (95%-BI) |
|---|---|---|
| PV1 | +2,3 [−0,7; +4,7] | +99% [+11%; +216%] |
| PV2 | +4,9 [−0,6; +11,7] | +97% [+6%; +204%] |
| PV3 | +5,8 [−1,4; +10,6] | +78% [−9%; +272%] |
| PV4 | +5,6 [−0,0; +11,0] | +77% [−11%; +258%] |
| PV5 | +4,2 [−0,6; +7,7] | +77% [−8%; +254%] |
| PV6 | +5,0 [−1,4; +9,4] | +76% [−12%; +259%] |
| PV7 | +6,0 [−0,5; +11,7] | +76% [−8%; +221%] |
| PV8 | +13,2 [−1,8; +30,9] | +74% [−24%; +235%] |

De geschatte heldere-weereffecten zijn positief, maar de intervallen voor `ΔT` omvatten nul voor alle panelen; bij `P_mpp` omvatten de intervallen nul voor PV3–PV8. De vermogensintervallen zijn zeer breed en de PV8-temperatuurschatting is instabiel. De uitkomsten ondersteunen dus de richting van de verwachting, maar zijn onvoldoende precies om het effect betrouwbaar vast te stellen. De waargenomen mediane MPP-waarden zijn bij helder weer hoger dan bij bewolkt weer voor alle labels; door duplicatie tussen PV4/PV5 en andere overeenkomsten is dit geen bewijs van acht onafhankelijke responsen.

### 5.3 Deel II — Paneeltemperatuur en elektrische prestaties

**Kernresultaat.** De ruwe paneeltemperatuur–`P_mpp`-correlaties zijn positief (r = 0,635 tot 0,896), maar instraling verhoogt tegelijk de fotostroom en verwarmt de module. Na correctie voor de beschikbare weers- en tijdvariabelen zijn de geschatte `ln(P_mpp)`-temperatuurhellingen nog steeds positief, wat voor gebruikelijk kristallijn silicium onverwacht is. Dit is geen bewijs dat opwarming het vermogen verhoogt. De `Voc`-hellingen zijn negatief maar onzeker; de onzekerheidsintervallen omvatten nul. Met de huidige sensorkwaliteit en kanaalonafhankelijkheid is een afzonderlijk temperatuureffect op de elektrische prestaties dus niet betrouwbaar vastgesteld.

#### 5.3.1 Ruwe elektrische correlaties per paneel

De tabel rapporteert Pearson-correlaties op geldige daglichturen (`G > 50 W/m²`) per module. De correlaties zijn niet gecorrigeerd voor andere variabelen. Per paneel verschilt het aantal complete uren; n is 80 voor PV1–PV7 en 51 voor PV8.

| Paneel | r(G,Pmpp) | r(G,ΔT) | r(T,Voc) | r(T,Isc) | r(T,Vmpp) | r(T,Impp) | r(T,FF) | r(T,Pmpp) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| PV1 | +0,912 | +0,794 | −0,038 | +0,752 | −0,518 | +0,757 | −0,203 | +0,750 |
| PV2 | +0,906 | +0,709 | +0,417 | +0,905 | −0,606 | +0,902 | −0,629 | +0,896 |
| PV3 | +0,729 | +0,896 | +0,059 | +0,232 | −0,285 | +0,688 | +0,683 | +0,688 |
| PV4 | +0,728 | +0,886 | +0,120 | +0,413 | −0,290 | +0,741 | +0,675 | +0,740 |
| PV5 | +0,728 | +0,887 | +0,009 | +0,293 | −0,303 | +0,637 | +0,707 | +0,635 |
| PV6 | +0,730 | +0,890 | +0,087 | +0,396 | −0,348 | +0,693 | +0,655 | +0,691 |
| PV7 | +0,946 | +0,796 | +0,320 | +0,812 | −0,282 | +0,896 | +0,460 | +0,896 |
| PV8 | +0,939 | +0,664 | +0,248 | +0,752 | −0,357 | +0,786 | +0,729 | +0,782 |

De positieve ruwe relatie tussen temperatuur en MPP-vermogen is bij alle panelen zichtbaar, maar volgt mede uit het feit dat instraling tegelijk temperatuur en fotostroom verhoogt. Dit is dus geen schatting van het geïsoleerde temperatuureffect. De tegengestelde of wisselende correlaties tussen temperatuur en Voc benadrukken waarom per-paneel correctie en meetkwaliteitscontrole nodig zijn.

#### 5.3.2 Paneelspecifieke gecorrigeerde regressies

De regressies zijn voor ieder paneel afzonderlijk geschat. De puntschatting en 95%-dagblok-bootstrapinterval staan hieronder. De dagbootstrap trekt volledige kalenderdagen 500 keer met teruglegging. Er worden geen beslissende p-waarden gebruikt: er zijn slechts 8–14 dagclusters per paneel en de panelen delen dezelfde weersomstandigheden.

| Paneel | n/dagen (ΔT; Voc; Pmpp) | ΔT per W/m² (95%-BI) | Voc per °C (95%-BI) | ln(Pmpp) per °C (95%-BI) |
|---|---|---|---|---|
| PV1 | 80/14; 80/14; 80/14 | +0,0266 [+0,0149; +0,0413] | −0,0479 [−0,0847; +0,0191] | +0,1089 [+0,0764; +0,1780] |
| PV2 | 80/14; 80/14; 80/14 | +0,0519 [+0,0376; +0,0683] | −0,0192 [−0,0507; +0,0308] | +0,0755 [+0,0586; +0,0935] |
| PV3 | 80/14; 77/14; 77/14 | +0,0661 [+0,0466; +0,0872] | −0,0191 [−0,0642; +0,0255] | +0,0615 [+0,0222; +0,0765] |
| PV4 | 80/14; 77/14; 77/14 | +0,0640 [+0,0471; +0,0805] | −0,0210 [−0,0648; +0,0266] | +0,0662 [+0,0232; +0,0827] |
| PV5 | 80/14; 77/14; 77/14 | +0,0479 [+0,0357; +0,0615] | −0,0276 [−0,0988; +0,0357] | +0,0757 [+0,0039; +0,1028] |
| PV6 | 80/14; 77/14; 77/14 | +0,0585 [+0,0441; +0,0738] | −0,0433 [−0,1051; +0,0200] | +0,0508 [−0,0189; +0,0807] |
| PV7 | 80/14; 53/13; 53/13 | +0,0552 [+0,0432; +0,0678] | −0,0526 [−0,1337; +0,0055] | +0,0417 [−0,0082; +0,0678] |
| PV8 | 51/11; 46/8; 46/8 | +0,0996 [+0,0069; +0,1810] | −0,0150 [−0,0472; +0,0063] | +0,0033 [−0,0147; +0,0180] |

Alle acht ΔT-hellingen zijn positief en alle bijbehorende bootstrapintervallen liggen boven nul. Alle Voc-hellingen zijn negatief, maar de intervallen omvatten nul. Dit past qua richting bij de gebruikelijke negatieve temperatuurrespons van silicium-PV [3], maar is onvoldoende bewijs voor een aantoonbaar effect in deze meetreeks. Alle `ln(Pmpp)`-puntschattingen zijn positief; vijf intervallen liggen boven nul. Dit teken is fysisch onverwacht en mag niet worden uitgelegd als een vermogensverhoging door opwarming. Resterende instralingsconfounding, de regionale stralingsproxy, elektrische kanaalproblemen of tijdsstructuur kunnen de uitkomst veroorzaken.

## 6. Discussie

### 6.1 Betekenis van de resultaten

De weeranalyse geeft een concreter, maar voorlopig antwoord. In de volledige KNMI-reeks hadden heldere daglichturen een hogere mediane globale straling dan bewolkte uren. Binnen de gekoppelde paneeluren was de mediane `ΔT` onder helder weer groter bij alle labels en was de MPP-mediaan hoger. De absolute paneeltemperatuur was niet consequent hoger, omdat de lokale buitenlucht tijdens de heldere matched uren juist koeler was. Dit onderscheid onderbouwt waarom `T_paneel` en `ΔT` apart zijn geanalyseerd. De wolkeneffectmodellen zijn echter breed onzeker, met slechts zes heldere meetdagen; zij wijzen de verwachte kant op, maar leveren geen nauwkeurige effectgrootte. Wind, montage, stralingshoek en afstand tussen Schiphol en Science Park blijven beperkingen.

Elektrische effecten zijn niet betrouwbaar te isoleren. De regressietekens van Voc en `Pmpp` zijn tegengesteld aan de eenvoudige verwachting voor veel silicium-PV-systemen; daarnaast veranderen schattingen bij een andere instralingsdrempel. De gegevens missen een betrouwbare lokale `GPOA`-meting, sensorkalibratie, onafhankelijke kanaalverificatie en paneldatasheets. De afzonderlijke paneelcoëfficiënten zijn daarom exploratieve associaties, geen gevalideerde modulecoëfficiënten. Een rendementvergelijking of rangorde blijft niet gerechtvaardigd.

### 6.2 Beperkingen

1. **Meetduur:** ongeveer 26 kalenderdagen in het bronbestand; elektrische/temp-koppeling voor het model beslaat 14 dagen.
2. **Pt100-herkomst:** twee tagfamilies zonder overlap en onbekende fysieke montage.
3. **PV8:** sterke temperatuurafwijkingen; oorzaak niet vastgesteld.
4. **Elektrische kanalen:** veel exacte overeenkomsten PV3–PV8; onafhankelijke meetkanalen niet bevestigd.
5. **Instraling:** CMP-10-eenheid en offset onbekend; KNMI-straling komt van Schiphol en is horizontaal.
6. **Tijdsresolutie:** KNMI per uur, solar op kortere intervallen; korte bewolkingsfluctuaties worden uitgevlakt.
7. **Specificaties:** paneeltechnologie, naamplaatvermogen, oppervlakte, oriëntatie, montage en fabrikanttemperatuurcoëfficiënten ontbreken.
8. **Onzekerheidsbegroting:** Type-B meetonzekerheden kunnen niet worden ingevuld zonder instrumentdata.
9. **Clustering:** slechts 14 dagclusters voor regressies; kleine steekproef maakt p-waarden en intervallen kwetsbaar.
10. **Reproduceerbaarheid:** voor uitvoering is de geautoriseerde ruwe CSV naast het notebook nodig; deze is bewust niet in de openbare repo of het downloadpakket opgenomen.

## 7. Conclusie

### 7.1 Deel I — Weer en paneeltemperatuur

In de volledige KNMI-daglichtreeks was de mediane globale straling hoger tijdens heldere dan tijdens bewolkte uren (253 tegenover 156 W/m²). In de gekoppelde, veel kleinere paneelreeks was de mediane `ΔT` bij helder weer hoger voor alle acht paneellabels. De absolute paneeltemperatuur was niet steeds hoger, omdat de lokale buitenlucht tijdens de heldere subset koeler was. De gecorrigeerde onzekerheidsintervallen voor het heldere–bewolkte `ΔT`-verschil omvatten nul voor alle panelen. Dit is een aanwijzing in de verwachte richting, maar geen nauwkeurige schatting van een weertype-effect.

### 7.2 Deel II — Paneeltemperatuur en elektrische prestaties

De ruwe temperatuur–`P_mpp`-correlaties zijn positief, maar vermengen het temperatuureffect met de invloed van instraling. In de paneelspecifieke modellen zijn de `Voc`-temperatuurhellingen negatief maar onzeker. De geschatte temperatuurhellingen van `ln(P_mpp)` zijn positief en fysisch onverwacht; zij vormen geen bewijs dat opwarming het vermogen verhoogt. Met deze data kan een zelfstandig causaal effect van paneeltemperatuur op de elektrische prestaties niet betrouwbaar worden vastgesteld.

**Antwoord op de onderzoeksvraag:** de metingen laten een richtinggevend verband zien tussen heldere omstandigheden, meer globale straling en een grotere paneelopwarming boven de buitenlucht. Voor het afzonderlijke effect van paneeltemperatuur op de elektrische prestaties blijft de uitkomst onbeslist. De korte gekoppelde reeks, regionale instralingsproxy, onzekere Pt100-mapping en mogelijke duplicatie van elektrische kanalen beperken de conclusie. De acht modules zijn afzonderlijk onderzocht, maar kunnen niet verantwoord worden gerangschikt.

## 8. Aanbevelingen

### 8.1 Direct nodig voor datavalidatie

1. Bevestig de sensor-paneel-mapping van alle Pt100-tagvarianten en verklaar het gat tussen beide Pt100-periodes.
2. Controleer PV8 fysiek: montageplaats, thermisch contact, bedrading, kanaalidentiteit en Pt100-weerstand/temperatuurconversie.
3. Vraag de logger-/DAQ-configuratie op en controleer of PV3–PV8 elektrische waarden onafhankelijke kanalen zijn.
4. Verifieer CMP-10-type, gevoeligheid, uitleeseenheid, offset, kalibratie en oriëntatie; vergelijk nachtelijke nulmetingen met de fabrikantverwachting.
5. Verzamel paneelfabrikant, celtechnologie, STC-vermogen, oppervlakte, azimut/helling, montage en temperatuurcoëfficiënten.
6. Verkrijg nauwkeurigheid, resolutie en kalibratie-informatie van stroom-, spannings-, temperatuur- en stralingskanalen.

### 8.2 Voor vervolgonderzoek

1. Gebruik een gekalibreerde pyranometer in het paneelvlak, gelijktijdig met lokale wind- en omgevingstemperatuur.
2. Meet gedurende meerdere seizoenen en verzamel I–V-curves of onafhankelijke MPP-traces met duidelijke tijdstempels.
3. Leg vooraf instrumentcorrecties, kwaliteitsgrenzen en weertypecriteria vast.
4. Na kanaalvalidatie: analyseer dagblokken met irradiance-normalisatie; rapporteer effectgrootten, bootstrapintervallen, aantal onafhankelijke dagen, residudiagnostiek en gevoeligheidsanalyses.
5. Publiceer pas na toestemming van HvA Energielab en AMOLF een gecontroleerde versie met geanonimiseerde/afgeleide resultaten.

## 9. Bronnen

1. Faiman, D. (2008). Assessing the outdoor operating temperature of photovoltaic modules. *Progress in Photovoltaics: Research and Applications, 16*(4), 307–315. https://doi.org/10.1002/pip.813
2. European Commission, Joint Research Centre. (z.d.). *Photovoltaic Geographical Information System (PVGIS): Data sources and calculation methods*. https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis/general-information/data-sources-calculation-methods_en
3. National Renewable Energy Laboratory. (z.d.). *System Advisor Model (SAM) Help: Photovoltaic module parameters*. https://samrepo.nlr.gov/help/pv_module.html
4. International Electrotechnical Commission. (2021). *IEC 60891:2021 — Photovoltaic devices: Procedures for temperature and irradiance corrections to measured I–V characteristics*. https://webstore.iec.ch/en/publication/61766
5. Koninklijk Nederlands Meteorologisch Instituut. (z.d.). *Uurwaarden van weerstations*. https://daggegevens.knmi.nl/klimatologie/uurgegevens
6. Taylor, B. N., & Kuyatt, C. E. (1994). *Guidelines for Evaluating and Expressing the Uncertainty of NIST Measurement Results* (NIST Technical Note 1297), Appendix A: Law of Propagation of Uncertainty. https://www.nist.gov/pml/nist-technical-note-1297/nist-tn-1297-appendix-law-propagation-uncertainty
7. Sandia National Laboratories, PV Performance Modeling Collaborative. (z.d.). *Faiman Module Temperature Model*. https://pvpmc.sandia.gov/modeling-guide/2-dc-module-iv/module-temperature/faiman-module-temperature-model/.
8. KNMI. (z.d.). *Uurwaarden van weerstations*. Definitie van bewolking `N` in achtsten en code 9 voor onbekende/bovenlucht onzichtbaar. https://www.daggegevens.knmi.nl/klimatologie/uurgegevens

KNMI-gegevens zijn met bronvermelding gebruikt. De ruwe SolarNL-export wordt niet als los bestand verspreid. De openbare website bevat de door de projectverantwoordelijke vrijgegeven afgeleide visualisaties; de volledige rekenbestanden en lokale invoer blijven in de onderzoekswerkmap.
