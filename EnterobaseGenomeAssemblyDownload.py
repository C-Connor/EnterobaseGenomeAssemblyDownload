#!/usr/bin/env python2

import urllib2
import base64
import json
import os
import logging
import traceback
import time
import sys
import time
import argparse
import getpass
import pipes

#get command line arguments
cl_parser = argparse.ArgumentParser(description="Downloads genome assemblies from enterobase when provided with a download list.")
cl_parser.add_argument("-l","--download-list",
    help="Path to text file containing assemblies to download.",
    dest="dlist",
    type=str)
cl_parser.add_argument("-o","--output",
    help="Specify output path to save assemblies",
    default=os.getcwd()+os.sep+"Enterobase_Assemblies"+time.strftime('%Y%m%d_%H%M'),dest="output",
    type=str)
cl_parser.add_argument("-a","--accession",
    help="Name downloaded fasta files by accession number rather than assembly barcode",
    action='store_true',dest="accession",
    required=False)
cl_parser.add_argument("--instructions",
    help="Print instructions for getting download text file and exit.",
    action='store_true',
    required=False,
    dest="instructions")
cl_parser.add_argument("-d","--database",
    help="Enterobase database to download assemblies from. (senterica, ecoli, yersinia, mcatarrhalis)",
    dest="db",
    type=str)

cl_args = cl_parser.parse_args()

if cl_args.instructions:
    print("\nInstructions for creating the download file from enterobase required by this script: \n\n"
        "1. Go to enterobase.warwick.ac.uk and select your database of interest. Select 'Search strains'. \n"
        "2. Search for your desired strains.\n"
        "3. Ensure that 'Experimental Data' in the top right corner, is set to 'Assembly Stats'.\n"
        "4. Download the text file by selecting 'Data > Save to Local File'.\n"
        "5. The resulting text file should contain columns corresponding to those on enterobase. There should also be a column called 'Assembly Barcode'.\n\n"
        "This script requires a valid enterobase login with API access to your database of interest.")
    sys.exit()

#check user input
if not cl_args.dlist:
    print("Error: argument -l / --download-list is required")
    sys.exit()
if not cl_args.db:
    print("Error: argument -d / --database is required")
    sys.exit()

if not os.path.isfile(cl_args.dlist):
    print('Could not find download list file.')
    print('Exiting')
    sys.exit()

cl_args.output = cl_args.output + os.sep
if not os.path.exists(os.path.dirname(cl_args.output)) and os.path.dirname(cl_args.output) != '':
    os.makedirs(os.path.dirname(cl_args.output))

#prompt for loging details
ENTEROBASE_USERNAME = pipes.quote(raw_input("Please enter Enterobase username: "))
ENTEROBASE_PASSWORD = pipes.quote(getpass.getpass("Please enter Enterobase password: "))

ENTEROBASE_SERVER = 'https://enterobase.warwick.ac.uk'
apiaddress = '%s/api/v2.0/login?username=%s&password=%s' %(ENTEROBASE_SERVER, ENTEROBASE_USERNAME, ENTEROBASE_PASSWORD)

#get API token
print('Retrieving API token.')
try:
    response = urllib2.urlopen(apiaddress)
    data = json.load(response)
    API_TOKEN = data['api_token']
except urllib2.HTTPError as Response_error:
    print("Connection error ocurred:")
    print '%d %s. <%s>\n Reason: %s' %(Response_error.code, Response_error.msg, Response_error.geturl(), Response_error.read())
    sys.exit()

assembly_error_log = list()
fasta_error_log = list()

def __create_request(request_str):
    request = urllib2.Request(request_str)
    base64string = base64.encodestring('%s:%s' % (API_TOKEN,'')).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    return request

#search header line for 'assembly barcode' string as sometimes it changes places
def barcode_search(header_line):
    count = 0
    while count <= len(header_line.split('\t')):
        try:
            if header_line.split('\t')[count].strip() == 'Assembly barcode':
                return(count)
            else:
                count += 1
        except IndexError:
            raise ValueError('Assembly barcode could not be found in header')

#search header line for 'Data Source(Accession No.;Sequencing Platform;Sequencing Library;Insert Size;Experiment;Status)'
def accession_search(header_line):
    count = 0
    while count <= len(header_line.split('\t')):
        try:
            if header_line.split('\t')[count].strip() == 'Data Source(Accession No.;Sequencing Platform;Sequencing Library;Insert Size;Experiment;Status)':
                return(count)
            else:
                count += 1
        except IndexError:
            raise ValueError('Data Source (...) could not be found in header')


assembly_codes = list()
assembly_dict = dict()
with open(cl_args.dlist,'r') as fin:
    header = fin.readline()
    indexer_barcode = barcode_search(header)
    indexer_accession = accession_search(header)
    for line in fin:
        assembly_codes.append(line.split('\t')[indexer_barcode].strip())
        assembly_dict[line.split('\t')[indexer_barcode].strip()] = line.split('\t')[indexer_accession].split(';')[0]

count = 1
fasta_error_count = 0
assembly_code_error_count = 0
while count < len(assembly_codes):
    time.sleep(5)
    querycode = assembly_codes[count]
    address = 'http://enterobase.warwick.ac.uk/api/v2.0/%s/assemblies?barcode=%s&limit=50' % (cl_args.db, querycode)
    try:
        response = urllib2.urlopen(__create_request(address))
        data = json.load(response)
        fasta_url = data['Assemblies'][0]['download_fasta_link']
        try:
            fasta_response = urllib2.urlopen(__create_request(fasta_url))
            if fasta_response.getcode() == 200:
                if cl_args.accession:
                    with open(cl_args.output+str(assembly_dict.get(assembly_codes[count])+'.fasta'),'w') as fasta_out:
                        fasta_out.write(fasta_response.read())
                else:
                    with open(cl_args.output+str(assembly_codes[count])+'.fasta','w') as fasta_out:
                        fasta_out.write(fasta_response.read())
            else:
                fasta_error_log.append([count, assembly_codes[count], fasta_url, fasta_response.getcode(), 'Failed download, bad server response.'])
        except urllib2.HTTPError as Response_error:
            fasta_error_log.append(['Count: '+str(count), 'Assembly code: '+str(assembly_codes[count]), 'Fasta URL: '+str(fasta_url), 'Reason:  %s, %s' %(Response_error.read(), Response_error.msg)])
            fasta_error_count = fasta_error_count + 1
    except urllib2.HTTPError as Response_error:
        assembly_error_log.append(['Count: '+str(count), 'Assembly code: '+str(assembly_codes[count]), 'Query address: '+str(address), 'Reason: %s, %s'%(Response_error.read(), Response_error.msg)])
        assembly_code_error_count = assembly_code_error_count + 1
    sys.stdout.write('\rProgress: %d out of %d' %(count, len(assembly_codes)-1))
    sys.stdout.flush()
    count = count + 1

with open(cl_args.output+'..'+os.sep+'assembly_code_error_log_'+time.strftime('%Y%m%d_%H%M')+'.txt','w') as assembly_error_out:
    for line in assembly_error_log:
        assembly_error_out.write("%s\n" % line)
with open(cl_args.output+'..'+os.sep+'fasta_error_log_'+time.strftime('%Y%m%d_%H%M')+'.txt','w') as fasta_error_out:
    for line in fasta_error_log:
        fasta_error_out.write("%s\n" % line)
print '\nComplete, there were %d assembly_code errors and %d fasta download errors.\nOpen assembly_error_log or fasta_error_log to view errors.' %(assembly_code_error_count, fasta_error_count)
