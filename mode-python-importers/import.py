#!/usr/bin/env python

import sys
import os
sys.dont_write_bytecode = True

import requests
import json
import csv
import optparse
import utils
import clean_csv as cc
import create_upload as cu
import create_table as ct
import poll_import_status as pis

def import_csv(TABLE_NAME,DESCRIPTION,URL):
    
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
            
            f = open(URL,"rt")
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
    status_link = ct.create_table(TABLE_NAME,DESCRIPTION,token,header)
    polling_response = pis.poll_import_status(status_link)
    
    response_status = polling_response['state']
    
    if response_status == "failed":
        response = polling_response['error_message']
        print ">>> Table creation failed."
        print ">>> Error message: %s" % response
    else:
        response = pis.lookup_table(TABLE_NAME)
        js = json.loads(response.text)
        web_url = js['_links']['web']['href']
        print ">>> Import successful."
        print ">>> Table location: %s" % web_url
    
    sys.exit()

def prompt_table_name():
    name = raw_input(">>> Enter table name: " )
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
    elif json.loads (response.text)['id'] == "not_found":
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

parser.add_option("--csv",dest="csv",help="The location of your CSV. Can be a URL or file. REQUIRED.")
parser.add_option("--name",dest="table_name",help="The name of your table name.")
parser.add_option("--desc",dest="description",help="The description for your table.")
parser.add_option("--no-prompt",dest="no_prompt",action="store_true",
    help="If called, you will not be prompted for a table name or description. If called and and a table name " +
    "or description is not provided, a name will be inferred and the description will be left blank.")

(options, args) = parser.parse_args()

if not options.csv:
    print ">>> No CSV provided."
    sys.exit()

URL = options.csv
TABLE_NAME = options.table_name
DESCRIPTION = options.description
NO_PROMPT = options.no_prompt

if TABLE_NAME == None and NO_PROMPT == True:
    TABLE_NAME = inferred_name(URL)
    print ">>> Inferred table name: %s" % TABLE_NAME
elif TABLE_NAME == None and NO_PROMPT == None:
    TABLE_NAME = prompt_table_name()
else:
    status = check_table_name(TABLE_NAME)
    if status == "invalid" or status == "taken":
        print ">>> Table name is %s." % status
        sys.exit()

if DESCRIPTION == None and NO_PROMPT == True:
    DESCRIPTION = ""
elif DESCRIPTION == None and NO_PROMPT == None:
    DESCRIPTION = raw_input(">>> Enter table description: ")

import_csv(TABLE_NAME,DESCRIPTION,URL)
