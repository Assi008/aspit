# aspit-opgave

### Opgaven
Brug Python til at samle relevante regnskabstal i en json fil.
Lav en simpel Streamlit app som præsenterer regnskabsdata

### Script 1
Lav et Python script "get_urls_with_cvr.py" som skriver [url.txt] ved at anvende Curl fra https://datacvr.virk.dk/artikel/system-til-system-adgang-til-regnskabsdata
Filen skal indeholde en liste af url på alle xbrl (xml) regnskaber for en virksomhed fremsøgt ved cvr-nummer.
Vi forventer at python scriptet er organiseret pænt i logiske funktioner med forklaringer og at scriptet indeholder 
if __name__ == "__main__":
    main()
scriptet skal anvende argparse og anvendes som:
get_urls_with_cvr.py <cvr_nummer>
# argpase anvendelse:
import argparse
parser = argparse.ArgumentParser(description="Handle single or multiple values.")
parser.add_argument("--cvr_nummer", nargs='+', type=str, help="A single cvr or a list of cvr_numbers.")

### Script 2
"xbrl_parser.py" tager som input [url.txt] og skriver som output regnskabstal for hvert regnskab. 
Debug og modificer "xbrl_parser.py" sådan at scriptet læser [url.txt] og skriver en output fil i JOSN format [cvr_nummer.json] med en struktureret præsentation af regnskabsdata for de forskellige år i virksomhedens historie. 
python xbrl_parser.py url.txt --debug (vil køre listen af url i url.txt sekventielt)
python xbrl_parser.py url.txt --debug --single (vil køre url i første linje i url.txt)
python xbrl_parser.py url.txt --debug --single (vil køre listen af url i url.txt på multiple tråde)

Scriptet skal indeholde noget fejlhåndtering. Dvs hvis der feks opstår fejl i at læse filer eller værdier eller parse/udpakke xml filer så skal der skrives en log over hvad der er er gået galt og programmeet skal fortsætte uden at fejle. 

### Script 3
Lav en Streamlit app hvor der findes et inputfelt hvor brugeren kan vælge en lokal [cvr_nummer.json] og som herefter viser en præsentation af regnskabstal i en tabel.
Det kan være smart at anvende Pandas her. 
I tabellen skal der også være links til pdf-filer for alle regnskaber (findes også på: https://datacvr.virk.dk/artikel/system-til-system-adgang-til-regnskabsdata) 

### Getting started (se example_files folder) 
Ekempel script der skriver en json fil fra en template: write_json.py
Run curl by:
curl -XGET http://distribution.virk.dk/offentliggoerelser/_search --data-binary @example_files/query.json -H 'Content-Type: application/json'
