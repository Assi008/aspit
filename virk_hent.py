import requests
import json
import argparse
import subprocess

def get_encoded_pass():
    result = subprocess.run(["python", "encode_pass.py"], capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()  # capture the Base64 encoded string
    else:
        raise ValueError("Error in running encode_pass.py!")

# Use the function
ENCODED_AUTH_STRING = get_encoded_pass()

HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {ENCODED_AUTH_STRING}="  # Using the generated Base64 encoded string
}

def fetch_cvr_data(cvr):
    url = "http://distribution.virk.dk/cvr-permanent/virksomhed/_search"
    data = {
        "query": {
            "term": {
                "Vrvirksomhed.cvrNummer": str(cvr)
            }
        }
    }
    return _fetch_data(url, data)

def fetch_produktionsenhed_data(pnummer):
    url = "http://distribution.virk.dk/cvr-permanent/produktionsenhed/_search"
    data = {
        "query": {
            "bool": {
                "must": [{
                    "term": {
                        "VrproduktionsEnhed.pNummer": str(pnummer)
                    }
                }]
            }
        }
    }
    return _fetch_data(url, data)

def fetch_deltager_data(enhedsnummer):
    url = "http://distribution.virk.dk/cvr-permanent/deltager/_search"
    data = {
        "query": {
            "bool": {
                "must": [{
                    "term": {
                        "Vrdeltagerperson.enhedsNummer": str(enhedsnummer)
                    }
                }]
            }
        }
    }
    return _fetch_data(url, data)

def _fetch_data(url, data):
    response = requests.post(url, headers=HEADERS, json=data)
    response.encoding = 'utf-8'  # Ensure the response is in UTF-8

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

def write_data_to_file(filename, data):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(description="Fetch and store data from CVR API.")
    parser.add_argument("cvr", type=int, help="CVR number to query.")
    args = parser.parse_args()
    
    cvr_results = fetch_cvr_data(args.cvr)
    pnummer_list = [penhed['pNummer'] for penhed in cvr_results['hits']['hits'][0]['_source']['Vrvirksomhed']['penheder']]
    enhedsnummer_list = [relation['deltager']['enhedsNummer'] for relation in cvr_results['hits']['hits'][0]['_source']['Vrvirksomhed']['deltagerRelation']]
    
    write_data_to_file('__virk.json', cvr_results)

    for enhedsnummer in enhedsnummer_list:
        deltager_results = fetch_deltager_data(enhedsnummer)
        
        if deltager_results and deltager_results.get('hits', {}).get('total', 0) > 0:
            write_data_to_file(f'__enhedsnummer_{enhedsnummer}.json', deltager_results)
            
    for pnummer in pnummer_list:
        produktionsenhed_results = fetch_produktionsenhed_data(pnummer)
        
        if produktionsenhed_results and produktionsenhed_results.get('hits', {}).get('total', 0) > 0:
            write_data_to_file(f'__p_nummer_{pnummer}.json', produktionsenhed_results)

if __name__ == "__main__":
    main()
