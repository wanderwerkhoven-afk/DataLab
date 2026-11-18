# SolarNL — onderzoek en reproductie

De SolarNL-website is een SPA met de inleiding, theoretisch kader, methode, data en aannames, resultaten per paneel, conclusie en bronnen. De resultatenpagina bevat interactieve Plotly-grafieken voor relaties tussen buitenlucht, paneeltemperatuur, vermogen en bewolkingsklasse.

## Onderzoeksbestanden

- [Onderzoeksverslag](Onderzoeksverslag.md)
- [Volledig onderzoeksnotebook](SolarNL_Onderzoek.ipynb)
- [Reproduceerbare analysemodule](solarnl_analysis.py)
- [Python-afhankelijkheden](requirements.txt)

## Notebook uitvoeren

1. Installeer Python en Jupyter.
2. Installeer de pakketten met `python -m pip install -r requirements.txt`.
3. Plaats alleen de geautoriseerde SolarNL-meetexport als `Datasheet_query_(10).csv` in deze map. Het gebruikte KNMI-uurbestand staat al in de repository.
4. Open Jupyter vanuit deze map en voer `SolarNL_Onderzoek.ipynb` uit.

De notebook bevat geen ruwe SolarNL-data. De geautoriseerde SolarNL-meetexport blijft een lokale invoer en staat niet in deze openbare repository. `knmi_hourly.csv` bevat de aanvullende openbare uurgegevens van KNMI-station 240; bron en variabeledefinities staan in het onderzoeksverslag. De reproduceerbare code verwerkt PV1–PV8 afzonderlijk, maakt de weertypevergelijkingen en gebruikt dagblok-bootstrapintervallen.

## Reikwijdte

De resultaten zijn verkennend. De korte meetperiode, de regionale instralingsproxy, ontbrekende kalibratie- en paneelspecificaties en mogelijke duplicatie van elektrische kanalen beperken causale uitspraken en onderlinge rangschikking van modules.
