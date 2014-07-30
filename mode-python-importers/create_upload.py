import sys
import os
sys.dont_write_bytecode = True

import utils
import requests
import json

def create_upload(body):
    cred = (utils.USERNAME,utils.SECRET)
    headers = {'content-type': 'application/json'}
    ENDPOINT = '/api/uploads'
    
    print ">>> Creating upload."
    
    r = requests.post(utils.HOST % ENDPOINT,auth=cred,data=body)
    js = json.loads(r.text)
    
    if r.status_code != 201 and r.status_code != 200:
        print ">>> Upload creation failed."
        print ">>> Response code: %i" % r.status_code
        print ">>> Error message: %s" % js['message']
        sys.exit()
    
    token = js['token']
    
    print ">>> Upload created."
    
    return token
    