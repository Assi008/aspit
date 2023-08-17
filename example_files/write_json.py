import json
import argparse

def cvr_query(cvrNummer,template_json,query_json):
    #read content of json file
    with open(template_json, 'r') as f:
        json_data = json.load(f)

    #write new cvrNummer json 
    json_data["query"]["bool"]["must"][0]["term"]["cvrNummer"]["value"]=cvrNummer

    #save as new file
    with open(query_json, 'w') as f:
        json.dump(json_data, f,indent=4)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cvr", help="cvr number")
    p.add_argument("template_json", help="template json query file")
    p.add_argument("query_file", default = "query.json", help="filename of the query file")
    args = p.parse_args()

    cvr_query(args.cvr,args.template_json,args.query_file)