#!/usr/bin/env python

import sys
import os
sys.dont_write_bytecode = True

import requests
import json
import csv
import codecs
import optparse
import utils
import clean_csv as cc
import create_upload as cu
import create_table as ct
import poll_import_status as pis

def import_csv(TABLE_NAME,DESCRIPTION,URL,REPLACE_EXISTING,ENCODING,IS_CLEAN):
    
    print ">>> Retrieving CSV."
    
    if URL.find("http") == 0: 
        r = requests.get(URL)
        
        if r.status_code == requests.codes.ok:
            print ">>> CSV successfully retrieved."
            text = r.text
            
        else:
            print ">>> Failed to get CSV. Returned status %i" % r.status_code
            print ">>> Error message: %s" % r.text
            sys.exit()
    
    else:
        try:
            if URL.find("~") == 0:
                URL =  os.path.expanduser(URL)
            
            f = codecs.open(URL,"rt",encoding=ENCODING)
            text = f.read()
            print ">>> File read successfully."
        
        except Exception as e:
            print ">>> Could not read file."
            print ">>> Error message: %s" % e
            sys.exit()
    
    table = cc.clean(text)
    header = table[0]
    body = table[1]
    
    token = cu.create_upload(body)
    status_link = ct.create_table(TABLE_NAME,DESCRIPTION,token,header,REPLACE_EXISTING,IS_CLEAN)
    polling_response = pis.poll_import_status(status_link)
    
    response_status = polling_response['state']
    
    if response_status == "failed":
        print polling_response
        response = polling_response['error_message']
        print ">>> Table creation failed."
        print ">>> Error message: %s" % response
    else:
        response = pis.lookup_table(TABLE_NAME)
        js = json.loads(response.text)
        web_url = js['_links']['web']['href']
        print ">>> Import successful."
        print ">>> Table location: %s" % web_url

def prompt_table_name(idx):
    name = raw_input(">>> Enter table name for table %i: " % idx)
    unique = False
     
    while unique == False:
        status = check_table_name(name)
        
        if status == "invalid":
            name = raw_input(">>> Table name invalid. Enter a new name: ")
        elif status == "taken":
            name = raw_input(">>> Table name already taken. Enter a new name: ")
        else:
            unique = True
    
    return name

def check_table_name(name):
    response = pis.lookup_table(name)
    
    if response.status_code == 200:
        return "taken"
    elif json.loads(response.text)['id'] == "not_found":
        return "valid"
    else:
        return "taken"

def inferred_name(url):
    lower = url.lower() 
    end = lower.find(".csv")
    
    if end == -1:
        end = len(lower)
    
    trim = lower[:end]
    rev = trim[::-1]
    
    start = rev.find("/")
    
    if start == -1:
        start = len(rev)
    
    rev_name = rev[:start]
    name = rev_name[::-1]
    
    return utils.normalize(name)

## START SCRIPT

parser = optparse.OptionParser()

parser.add_option("--csv",dest="csv",help="REQUIRED. The location of your CSV. Can be a URL or file. Multiple CSVs can be imported " +
    "in the same command. To import multiple CSVs, separate their URLs or paths by commas.")
parser.add_option("--name",dest="table_name",help="The name of your table name.")
parser.add_option("--desc",dest="description",help="The description for your table.")
parser.add_option("--no-prompt",dest="no_prompt",action="store_true",
    help="If called, you will not be prompted for a table name or description. If called and and a table name " +
    "or description is not provided, a name will be inferred and the description will be left blank.")
parser.add_option("--replace",dest="replace_existing",action="store_true",
    help="If called and you provide a table name that already exists, your new CSV will replace the exsiting " +
    "table. Note that this action cannot be undone.")
parser.add_option("--encoding",dest="encoding",
    help="Set character encoding for file you're reading. If not set, defaults to UTF-8.")
parser.add_option("--clean",dest="clean",action="store_true",
    help="Set flag if data is clean and can be imported exactly as is. If not set, " +
    "Mode will parse and partially clean data.")

(options, args) = parser.parse_args()

if not options.csv:
    print ">>> No CSV provided."
    sys.exit()

URLS = options.csv
TABLE_NAMES = options.table_name
DESCRIPTIONS = options.description
NO_PROMPT = options.no_prompt
REPLACE_EXISTING = options.replace_existing
ENCODING = options.encoding
CLEAN = options.clean
    
url_list = URLS.split(",")
url_count = len(url_list)

if TABLE_NAMES == None:
    table_list = [None] * url_count
else:
    table_list = TABLE_NAMES.split(",")
    table_count = len(table_list)
    
    if table_count < url_count:
        table_list = table_list + [None] * (url_count - table_count)

if DESCRIPTIONS == None:
    description_list = [None] * url_count
else:
    description_list = DESCRIPTIONS.split(",")
    description_count = len(description_list)
    
    if description_count < url_count:
        description_list = description_list + [None] * (url_count - description_count)

for idx,URL in enumerate(url_list):
    
    print "STARTING TABLE %i." % idx
    
    TABLE_NAME = table_list[idx]
    DESCRIPTION = description_list[idx]
    
    if TABLE_NAME == None and NO_PROMPT == True:
        TABLE_NAME = inferred_name(URL)
        print ">>> Inferred table name for table %i: %s" % ((idx + 1),TABLE_NAME)
    
    elif TABLE_NAME == None and NO_PROMPT == None:
        TABLE_NAME = prompt_table_name((idx + 1))
    else:
        status = check_table_name(TABLE_NAME)
        if status == "invalid" or (status == "taken" and REPLACE_EXISTING == None):
             print ">>> Table name for table %i is %s." % ((idx + 1),status)
             sys.exit()
    
    if DESCRIPTION == None and NO_PROMPT == True:
        DESCRIPTION = ""
    elif DESCRIPTION == None and NO_PROMPT == None:
        DESCRIPTION = raw_input(">>> Enter table description for table %i: " % (idx + 1))
    
    if URL.find("http") == 0:
        DESCRIPTION = DESCRIPTION + " Source: %s" % URL
        DESCRIPTION = DESCRIPTION.strip()
    
    if ENCODING == None:
        ENCODING = "utf-8"
    
    if CLEAN == None:
        CLEAN = 0
    else:
        CLEAN = 1
    
    import_csv(TABLE_NAME,DESCRIPTION,URL,REPLACE_EXISTING,ENCODING,CLEAN)
    
    print "TABLE %i COMPLETE." % idx

print "IMPORT COMPLETE."
sys.exit()