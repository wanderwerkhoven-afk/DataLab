# SolarNL — Onderzoeksverslag (werkversie 0.1)

**Project:** Solar Field data-analyse, HvA Energielab en AMOLF  
**Locatie:** Science Park 104, Amsterdam  
**Onderzoeksperiode in de beschikbare export:** 23–27 oktober 2026 (UTC)  
**Status:** onderzoek in uitvoering; resultaten zijn voorlopig en niet gevalideerd door opdrachtgever.

## 1. Onderzoeksvraag
*Onderzoek wat de invloed is van verschillende weersomstandigheden op de elektrische prestaties van de acht zonnepanelen. Onderzoek hierbij hoe verschillende weertypen de temperatuur van de zonnepanelen beïnvloeden en welk effect deze temperatuur heeft op de elektrische prestaties.*

De formulering volgt de oorspronkelijke opdrachtomschrijving (SolarField2_Opdracht_Omschrijving.docx).

### Deelvragen
1. Welke weersvariabelen zijn beschikbaar, wat is hun meetkwaliteit en wat ontbreekt?
2. Hoe verhouden paneeltemperaturen zich tot de omgevingstemperatuur en hoe varieert dit in de tijd?
3. Welke verbanden zijn zichtbaar tussen paneeltemperatuur, openklemspanning (Voc), fill factor (FF) en maximum-power-pointvermogen (Pmpp)?
4. In hoeverre kunnen verschillen tussen panelen verklaard worden door weersomstandigheden, in plaats van meetopstelling of paneeltechnologie?
5. Welke uitspraken zijn wetenschappelijk verantwoord met deze meetperiode en meetdekking?

## 2. Opzet en databronnen
De primaire databron is een InfluxDB-export met weerstationmetingen (PVMET500) en registraties van acht PV-apparaten. We werken in UTC om fouten rond tijdzone en wintertijd te vermijden. Het reproduceerbare analyseprotocol en de interactieve figuren staan in [SolarNL_Onderzoek.ipynb](SolarNL_Onderzoek.ipynb).

Het weerstation bevat omgevingstemperatuur, relatieve luchtvochtigheid en luchtdruk. De paneeldata bevatten Pt100-temperatuur en — wanneer beschikbaar — Isc, Impp, Vmpp, Voc en FF. CMP-10 is **vermoedelijk** een instralingssensor; identiteit, eenheid, offset en kalibratie moeten nog bevestigd worden. Aanvullende openbare weergegevens (wind, bewolking, neerslag) zijn nog niet geïntegreerd.

## 3. Datavoorbewerking en kwaliteitscontrole
- Parseer de InfluxDB-export per tabel; controleer delimiter, tijdstempels, labels en numerieke typen.
- Behoud ruwe omgevingstemperatuur in `Temperature-PVMET500_raw`. Vervang waarden boven 40 °C door het gemiddelde van de dichtstbijzijnde geldige buur vóór en na de fout; bij ontbrekende buur wordt de waarde onbekend (NaN). De grens is een projectmatige kwaliteitsregel.
- Synchroniseer de weer- en paneelmetingen met de dichtstbijzijnde weersensorregistratie binnen twee minuten.
- Bereken `delta_T = Pt100 − T_omgeving` in °C en `P_mpp = Impp × Vmpp` in W.
- Controleer meetdekking per paneel en per dag, interne consistentie van FF en gelijktijdige identieke elektrische waarden tussen panelen.
- Voer regressies alleen uit op gekoppelde, geldige meetparen en rapporteer aantallen. Interpretatie van correlaties is beschrijvend, niet causaal.

## 4. Voorlopige resultaten
**Temperatuur.** De tijdreeksen en boxplots in figuren 4a–4c laten zien hoe Pt100 en omgevingstemperatuur verschillen. De eerder gesignaleerde afwijkende waarden van PV8 vereisen een fysieke sensorcontrole voordat die reeks voor paneelvergelijking wordt gebruikt.

**Elektrische prestaties.** Figuren 5a–5c tonen de beschrijvende samenhang van paneeltemperatuur met Voc, FF en Pmpp. Figuur 11a voegt een lineaire Voc-temperatuurregressie toe. De regressie is ongecorrigeerd voor instraling en daarom geen directe meting van de temperatuurcoëfficiënt.

**Datakwaliteit.** De beschikbare meetexport bevat een ongelijke verdeling van elektrische metingen tussen panelen. Voor PV7 en PV8 zijn beduidend minder elektrische metingen aanwezig dan voor PV1 en PV2. Figuur 9a kwantificeert dit per dag. Figuur 10a vergelijkt gerapporteerde en berekende FF. Figuur 12a toont mogelijke overeenkomsten tussen elektrische kanalen.

**Instraling.** CMP-10-waarden zijn nog niet gevalideerd. Gebruik deze reeks daarom nog niet om een fysisch instralingsrendement of een genormaliseerde prestatievergelijking te rapporteren.

## 5. Fysische achtergrond en hypothesen
Een PV-module ontvangt zonnestraling en zet een deel daarvan om in elektrische energie. De moduletemperatuur hangt onder meer af van instraling, omgevingstemperatuur, convectieve koeling (wind), stralingsuitwisseling en constructie. Bij veel silicium-PV-technologieën neemt Voc af met stijgende celtemperatuur, maar de gemeten samenhang kan door gelijktijdige veranderingen in instraling vertekend worden.

Hypothese H1: hogere instraling hangt samen met een hogere paneeltemperatuur ten opzichte van de lucht, mits de CMP-10-metingen betrouwbaar zijn.  
Hypothese H2: na correctie voor instraling is Voc bij hogere paneeltemperatuur gemiddeld lager, afhankelijk van paneeltechnologie.  
Hypothese H3: verschillen in gemeten Pmpp tussen panelen zijn niet interpreteerbaar als rendementverschillen zonder paneelspecificaties, correcte kanaaltoewijzing en instralingsnormalisatie.

Dit zijn **toetsbare hypothesen**, geen bewezen resultaten.

## 6. Beperkingen
De huidige export beslaat enkele dagen; dit is onvoldoende voor uitspraken over seizoenseffecten of meerjarige degradatie. Het ontbreken van geverifieerde instraling, windsnelheid en paneelspecificaties beperkt de interpretatie. Ongelijke meetdekking, mogelijke kanaalduplicatie en Pt100-afwijkingen kunnen vergelijkingen vertekenen. Tijdsafhankelijke metingen zijn doorgaans autocorreleerd; standaard p-waarden uit eenvoudige regressies zijn daarom niet zonder meer geldig voor hypothesetoetsing.

## 7. Benodigde validatie
1. Bevestig CMP-10-sensortype, kalibratie, offset, eenheid en tijdregistratie.
2. Bevestig Pt100-montage en sensor-paneelkoppeling, met nadruk op PV8.
3. Verifieer of de elektrische kanalen van de acht panelen onafhankelijk zijn.
4. Lever paneelspecificaties: fabrikant, technologie, nominaal vermogen, oppervlakte, hellingshoek, azimut en STC-temperatuurcoëfficiënten.
5. Verkrijg aanvullende weersgegevens voor wind, neerslag en bewolking, indien beschikbaar.

## 8. Volgende analysetrap
Na validatie van de instraling: (a) weerclassificatie op basis van expliciete meteorologische criteria; (b) dag- en paneelvergelijkingen onder vergelijkbare instraling; (c) multivariabele analyse van temperatuur en elektrische prestaties, met tijdsafhankelijke onzekerheid; (d) gevoeligheidsanalyse voor uitschieters en kanaalproblemen; (e) definitieve conclusies per deelvraag.

## 9. Figuurregister
- **4a** Pt100- en omgevingstemperatuur over tijd, °C.
- **4b** verdeling van ΔT per paneel, °C.
- **4c** ΔT per paneel over tijd, °C.
- **5a–c** Voc (V), FF (vermoedelijk %) en Pmpp (W) tegen Pt100 (°C).
- **6** CMP-10-tijdreeks, eenheid voorlopig niet bevestigd.
- **9a** meetdekking per paneel en dag (aantal).
- **10a** gerapporteerde en berekende FF.
- **11a** Voc versus Pt100 met ongecorrigeerde regressielijnen.
- **12a** percentage exact gelijke Impp-waarden tussen panelen.

## 10. Bronnen en bronverantwoording
- *SolarField2_Opdracht_Omschrijving.docx*, oorspronkelijke projectopdracht, HvA Energielab / AMOLF.
- *SolarNL_Onderzoek.ipynb*, reproduceerbare Python-analyses en figuren.
- *Datasheet_query_(10).csv*, primaire meetexport (vertrouwelijk; niet voor publieke verspreiding zonder toestemming).

**Publicatievoorbehoud:** de opdracht vermeldt dat studenten de data niet met derden delen. Het openbare GitHub-repositorybestand met ruwe meetgegevens moet daarom met de opdrachtgever worden afgestemd. Een `.gitignore` verwijdert geen reeds gepubliceerde data uit Git-geschiedenis.

**Belangrijk:** dit is een onderzoeksverslag in opbouw. Numerieke conclusies, onzekerheidsintervallen en definitieve antwoorden worden pas toegevoegd na uitvoering en validatie van de analyse op de definitieve brondata.
