import sys
sys.dont_write_bytecode = True

import requests
import utils
import json
import time
from threading import Thread

def poll_import_status(href):
    cred = (utils.USERNAME,utils.SECRET)
    polling_link = utils.HOST % href
    
    message = ">>> Current status: %s"
    
    running = True
    while running == True:
        
        r = requests.get(polling_link,auth=cred)
        response = json.loads(r.text)
        status = response['state']
        
        print message % status
        
        if status != "enqueued" and status != "running":
            running = False
        else: 
            running = True
        
        time.sleep(2)
    
    return response

def lookup_table(name):
    cred = (utils.USERNAME,utils.SECRET)
    
    r = requests.get(utils.HOST % ("/api/" + utils.USERNAME + "/tables/" + name),auth=cred)
    
    return r