import os
import pandas as pd
from airtable import airtable


def get_airtable():
    """Set Airtable access parameters for Govbase"""

    assert os.path.isfile('api_key.txt'), "Save your Airtable API key in api_key.txt to pull data directly from Airtable"

    BASE_ID = 'appx3e9Przn9iprkU'
    with open('api_key.txt', 'r') as f:
        API_KEY = f.readline().strip()
        
    return airtable.Airtable(BASE_ID, API_KEY)


def get_table_as_df(at, tableName, kwargs=None):
    """Get all records in a table and load into DataFrame"""
    
    if kwargs is None:
        kwargs = {}

    # Get all records
    records = []
    for r in at.iterate(tableName, **kwargs):
        records.append({'id': r['id'], **(r['fields'])})
        
    # Convert to DataFrame
    df = pd.DataFrame(records).set_index('id')
    
    return df
