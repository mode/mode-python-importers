import sys
import os
sys.dont_write_bytecode = True

import requests
import utils
import json

def create_table(name,description,token,column_headers,replace_existing):
    
    cred = (utils.USERNAME,utils.SECRET)
    header = {'content-type': 'application/json'}
    
    upload_request = create_request(name,description,token,column_headers)
    json_request = json.dumps(upload_request)
    
    post_url = utils.HOST % ("/api/" + utils.USERNAME + "/tables")
    
    print ">>> Creating table at %s" % post_url    
    r = requests.post(post_url,auth=cred,headers=header,data=json_request)
    process = "creation"
    
    if r.status_code == 400 and replace_existing == True:
        
        print ">>> Table already exists. Replacing existing table."
        r = replace_request(utils.HOST,utils.USERNAME,cred,header,json_request)
        process = "replacement"
    
    
    if r.status_code != 202:
        
        print ">>> Table %s failed. Returned status code %i" % (process, r.status_code)
        try:
            js = json.loads(r.text)
            response = js['message']
            print ">>> Error message: %s" % response
        except:
            print ">>> Full response:"
            print ""
            print r.text
        
        sys.exit()
        
    else:
        js = json.loads(r.text)
        state = js['state']
        self_link = js["_links"]["self"]["href"]
        
        print ">>> Beginning table %s." % process
        print ">>> Check status at %s" % (utils.HOST % self_link)
        print ">>> Current status: %s" % state
        
        return self_link

def create_request(name,description,token,column_headers):
    
    columns = []
    for h in column_headers:
        col = {"name":h['cleaned'] , "type":h['type']}
        columns.append(col)
    
    body = {
      "upload_token": token,
      "table": {
        "name": name,
        "description": description,
        "columns": columns
      }
    }
    
    return body

def replace_request(host,username,credentials,header,json_request):
    js = json.loads(json_request)
    
    table_name = js['table']['name']
    del js['table']['name']
    
    request_body = json.dumps(js)
    request_url = post_url = host % ("/api/" + username + "/tables/" + table_name)
    
    r = requests.put(request_url,auth=credentials,headers=header,data=json_request)
    
    return r