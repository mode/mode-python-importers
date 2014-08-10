import sys
import os
sys.dont_write_bytecode = True

import random
import csv
import re
import utils
from dateutil.parser import *
from datetime import datetime
from tabulate import tabulate
import math

def clean(text):
    table = get_table(text)
    headers = table[0]
    body = table[1]
    body = body.encode("utf-8").strip()
    
    headers_clean = clean_headers(headers)
    
    print ">>> Parsing column types."
    
    results = add_column_types(headers_clean,body)
    
    headers_all = results[0]
    row_count = results[1]
    
    table = make_table(headers_all,row_count)
    
    print ">>> Displaying formatted column names and types:"
    print ""
    print tabulate(table)
    print ""
    
    return headers_all,body

def get_table(text):
    rows = text.splitlines()
    headers = rows[0]
    body_start = text.find(rows[1])
    body = text[body_start:]
    
    return headers, body

def clean_headers(headers):
    for line in csv.reader([headers], skipinitialspace=True):
        header_arr = line
    
    cleaned = []
    
    for idx,h in enumerate(header_arr):
        
        normalized = utils.normalize(h)
        ent = {"key":idx,"original":h,"cleaned":normalized}
        cleaned.append(ent)
    
    return cleaned

def add_column_types(headers,body):
    rows = body.splitlines()
    row_count = len(rows)
    
    sample_numbers = get_sample_numbers(row_count)
    sample = get_sample(rows,sample_numbers)
    
    for h in headers:
        col_num = h['key']
        guessed_type = check_type(col_num,sample)
        h['type'] = guessed_type[0]
        h['dist'] = guessed_type[1]
        
    return headers,row_count

def get_sample_numbers(rows):
    sample_ratio = utils.SAMPLE
    sample_size = int(math.ceil(sample_ratio*rows))
    
    sample_rows = []
    
    for n in range(0,sample_size):
        sample = random.randrange(0,rows,1)
        sample_rows.append(sample)
    
    return sample_rows

def get_sample(rows,sample_numbers):
    sample = []
    
    for n in sample_numbers:
        sample.append(rows[n])
    
    return sample

def check_type(column,sample_rows):
    values = []
    
    for s in sample_rows:
        for line in csv.reader([s], skipinitialspace=True):
            cells = line
        
        cell = cells[column]
        values.append(cell)
    
    type_arr = check_each_row(values)
    guessed_type = calculate_type(type_arr)
    
    return guessed_type, type_arr

def check_each_row(arr):
    type_arr = {"str":0,"number":0,"date":0,"bool":0,"null":0}
    
    for a in arr:
        parsed_type = parseValue(a)
        type_arr[parsed_type] += 1
        
    return type_arr

def parseValue(value):
    
    if value == "":
        return "null"
    
    else:
        
        val = type(value).__name__
        
        if val == "int" or val == "float" or val == "long":
            return "number"
        elif val == "bool":
            return "bool"
        elif val == "datetime":
            return "date"
        elif val == "str":
            
            try:
                dummy = float(value)
                return "number"
            except:
                None
            
            try:
                for format in ['%Y-%m']:
                    result = datetime.strptime(value, format)
                return "str"
            except:
                None
                
            try:
                dummy = parse(value)
                return "date"
                
            except:
                None
            
            if value.lower() in ['true','t','false','f']:
                return "bool"
            
            # elif value.lower() in ['null','none']:
            #     return "null"
            
            else:
                return "str"
        
        else:
            return "str"

def calculate_type(type_arr):
    s = type_arr["str"]
    n = type_arr["number"]
    b = type_arr["bool"]
    d = type_arr["date"]
    u = type_arr["null"]
    
    if min(s,1) + min(n,1) + min(b,1) + min(d,1) > 1:
        return "string"
    elif n > 0:
        return "number"
    elif b > 0:
        return "boolean"
    elif d > 0:
        return "date"
    else:
        return "string"

def make_table(headers_all,row_count):
    sample_ratio = utils.SAMPLE
    sample_size = int(math.ceil(sample_ratio*row_count))
    
    table = []
    head = ["new_column_name","orig_column_name","guessed_type","string","date","number","boolean","null"]
    breakline = ["   ","   ","   ","   ","   ","   ","   ","   "]
    table.append(head)
    table.append(breakline)
    
    def r(string):
        return re.sub("^0.0%","--",string)
    
    for h in headers_all:
        strs =      "{0:.1f}%".format(1.*h['dist']['str']/sample_size * 100)
        dates =     "{0:.1f}%".format(1.*h['dist']['date']/sample_size * 100)
        numbers =   "{0:.1f}%".format(1.*h['dist']['number']/sample_size * 100)
        bools =     "{0:.1f}%".format(1.*h['dist']['bool']/sample_size * 100)
        nulls =     "{0:.1f}%".format(1.*h['dist']['null']/sample_size * 100)
        
        row = [h['cleaned'],h['original'],h['type'],r(strs),r(dates),r(numbers),r(bools),r(nulls)]
        table.append(row)
    
    return table