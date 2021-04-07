import os
import sys
import argparse

import pandas as pd

from datetime import datetime

from sodapy import Socrata

from config import mappings as es_mappings    
from elastic_helper import (
    ElasticHelperException, 
    insert_doc,
    try_create_index
)

DATASET_ID = "nc67-uf89"
APP_TOKEN = os.environ.get("APP_TOKEN") 
ES_HOST = os.environ.get("ES_HOST")
ES_USERNAME = os.environ.get("ES_USERNAME")
ES_PASSWORD = os.environ.get("ES_PASSWORD")

if __name__ == '__main__':
    my_parser=argparse.ArgumentParser()
    my_parser.add_argument('--page_size', action='store', type=int, required=True)
    my_parser.add_argument('--num_pages', action='store', type=int)
    
    args = my_parser.parse_args(sys.argv[1:])
        
    page_size=args.page_size
    num_pages=args.num_pages
    
    limit=args.page_size
        
    client = Socrata(
        "data.cityofnewyork.us",
        APP_TOKEN,
    )
    
    try:
        try_create_index(
            "parking",
            ES_HOST,
            mappings=es_mappings,
            es_user=ES_USERNAME,
            es_pw=ES_PASSWORD,
        )
    except ElasticHelperException as e:
        print("Index already exists!")
        print(f"{e}")

for x in range(num_pages):
    rows = client.get(DATASET_ID, limit=page_size, offset=limit*x, order = ":id")
    
    for row in rows:
        try:
            row['issue_date']=datetime.strptime(row['issue_date'],"%m/%d/%Y").strftime("%Y/%m/%d")
            row['issue_date']=str(row['issue_date'])
            row['summons_number']=float(row['summons_number'])
            
            ret = insert_doc(
            "parking",
            ES_HOST,
            data=row,
            es_user=ES_USERNAME,
            es_pw=ES_PASSWORD,
            )
            
        except Exception as e:
            print(f"Skipping! Failed to transform row: {row}. Reason: {e}")
            continue
