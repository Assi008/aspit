import gzip
import urllib.request
from lxml import etree
import argparse
from multiprocessing import Pool

def get_prefix(root, namespace_uri):
    # Find the prefix for the namespace
    prefix = [k for k, v in root.nsmap.items() if v == namespace_uri]

    if prefix:
        prefix = prefix[0]
    else:
        prefix = None

    return prefix

def find_value(tag, prefix, namespace, root):
    # Finding the first item with the given tag
    item = root.find(f'.//{prefix}:{tag}', namespaces={f'{prefix}': namespace})
    
    # Extracting the value if the item is found
    if item is not None:
        try:
            value = item.text
            return value
        except ValueError:
            print(f"Could not convert value for tag {tag}")
            return None
    else:
        print(f"Tag {tag} not found")
        return None

def financial_figures(url):
    # Get the XML data from the url
    response = urllib.request.urlopen(url)
    xml_data = response.read()
    # Decode the XML data if it is compressed
    if response.info().get('Content-Encoding') == 'gzip':
        xml_data = gzip.decompress(xml_data)
    # Parse the XML data
    try:
        root = etree.XML(xml_data)
        tree = etree.fromstring(xml_data)
    except etree.XMLSyntaxError:
        print(f"Could not parse XML data from url {url}")
        return

    # Find the prefix for the namespaces  
    fsa_prefix = get_prefix(root, 'http://xbrl.dcca.dk/fsa')
    gsd_prefix = get_prefix(root, 'http://xbrl.dcca.dk/gsd')
    fsa_namespace = root.nsmap[fsa_prefix]
    gsd_namespace = root.nsmap[gsd_prefix]

    # Find the reporting period dates
    periode_start = find_value('ReportingPeriodStartDate',gsd_prefix,gsd_namespace,root)
    periode_slut = find_value('ReportingPeriodEndDate',gsd_prefix,gsd_namespace,root)
    cvr_nummer = find_value('IdentificationNumberCvrOfReportingEntity',gsd_prefix,gsd_namespace,root)

    # Find the financial key numbers
    nettoomsaetning=find_value('Revenue',fsa_prefix,fsa_namespace,root)
    bruttofortjaeneste = find_value('GrossProfitLoss',fsa_prefix,fsa_namespace,root)
    # Search for GrossResult if GrossProfitLoss is not found
    if not bruttofortjaeneste:
        bruttofortjaeneste = find_value('GrossResult',fsa_prefix,fsa_namespace,root)
    aaretsresultat=find_value('ProfitLoss',fsa_prefix,fsa_namespace,root)
    egenkapital = find_value('Equity',fsa_prefix,fsa_namespace,root)
    balance = find_value('Assets',fsa_prefix,fsa_namespace,root)
    aktiver=find_value('Assets',fsa_prefix,fsa_namespace,root)
    kortfristet_gaeld=find_value('ShorttermLiabilitiesOtherThanProvisions',fsa_prefix,fsa_namespace,root)

    # Find the currency code 
    # Iterate through all measure elements using the correct namespace
    #TODO: This is ugly. Find a better way to do this
    for measure_tag in root.xpath(".//xbrli:measure", namespaces={'xbrli': 'http://www.xbrl.org/2003/instance'}):
        # Check if the text content contains "iso4217:"
        if "iso4217:" in measure_tag.text:
            # Split the text content at the colon and take the second part to get the currency code
            currency_code = measure_tag.text.split(":")[1]

    # Calculate the financial ratios
    #TODO: make better error handling
    likviditetsgrad, afkastningsgrad, soliditetsgrad = None, None, None
    
    if kortfristet_gaeld != None and kortfristet_gaeld != 0:
        likviditetsgrad = int(aktiver) / int(kortfristet_gaeld)
    if aktiver != None and aktiver != 0:
        afkastningsgrad = int(aaretsresultat) / int(aktiver)
        soliditetsgrad = int(egenkapital) / int(aktiver)

    # Create a dictionary with the financial data
    #TODO: Add more financial data (see proff.dk)
    financial_data = {
        'cvr_nummer': (cvr_nummer),
        'preiode_start': (periode_start),
        'periode_slut' : (periode_slut),
        'nettoomsaetning': (nettoomsaetning),
        'bruttofortjeneste': (bruttofortjaeneste),
        'aaretsresultat': (aaretsresultat),
        'egenkapital': (egenkapital),
        'balance': (balance),
        'valutakode': currency_code,
        'likviditetsgrad': likviditetsgrad,
        'afkastningsgrad': afkastningsgrad,
        'soliditetsgrad': soliditetsgrad
    }

    return financial_data

def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file.readlines()]
    return urls

def process_url(url):
    if args.debug:
        print(f"Processing URL: {url}")
    financial_data = financial_figures(url)
    if args.debug:
        print(financial_data)  # Print data in debug mode

def main():
    global args  # Make args accessible in process_url
    parser = argparse.ArgumentParser(description="Retrieve financial figures from a list of URLs.")
    parser.add_argument("input_file", help="Path to the file containing the URLs.")
    parser.add_argument("-d", "--debug", help="Enable debug mode.", action="store_true")
    parser.add_argument("-s", "--single", help="Run a single file from the input file.", action="store_true")
    args = parser.parse_args()

    urls = read_urls_from_file(args.input_file)
    
    if args.single:
        urls = [urls[0]]  # Only process the first URL

    if args.debug:
        # Process URLs sequentially in debug mode
        for url in urls:
            process_url(url)
    else:
        # Process URLs in parallel
        #TODO: Find a way to print the data in debug mode
        #TODO: Check if this works
        with Pool() as pool:
            pool.map(process_url, urls)

if __name__ == "__main__":
    main()

