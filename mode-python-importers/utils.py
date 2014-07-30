import yaml
import re
import requests
import json
import sys

def normalize(string):
    clean = " ".join(string.split())        # remove trailing, leading, duplicate whitespace
    
    clean = clean.lower()                   # lowercase
    clean = re.sub("\.", "_",clean)         # no periods
    clean = re.sub("-", "_",clean)          # no hyphens
    clean = re.sub("[^\w\s_]", "",clean)    # whitelist characters
    clean = re.sub("\s", "_",clean)         # no spaces
    clean = re.sub("_+", "_",clean)         # no multiple consecutive underscores
    clean = re.sub("(^_)|(_$)", "",clean)   # no leading or trailing underscores
    
    if len(clean) >= 64:
      clean = clean[0,63]
    
    return clean

def get_username(token,secret,host):
    cred = (token,secret)
    # headers = {'content-type': 'application/json'}
    ENDPOINT = '/api/account'
    
    print ">>> Retriving account info."
    
    response = requests.get(host % ENDPOINT,auth=cred)
    
    if response.status_code == 401:
         print ">>> Access denied. Please check your authorization credentials in the config.py file."
         sys.exit()
         
    js = json.loads(response.text) 
    username = js['username']
    
    return username

## CREDENTIALS SCRIPT
yml = yaml.load(open("config.yml", 'r'))

try:
    HOST = yml['host']
except:
    HOST = "https://modeanalytics.com%s"

TOKEN = yml['auth']['token']
SECRET = yml['auth']['secret']
USERNAME = get_username(TOKEN,SECRET,HOST)

try:
    SAMPLE = yml['sample_size']
except:
    SAMPLE = .3


    