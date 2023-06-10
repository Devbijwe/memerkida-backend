# from __init__ import params

from sqlalchemy import inspect
import os
from sqlalchemy_utils import database_exists, create_database
import json
with open("config.json","r") as c:
    params=json.load(c)['params']
# with open("config.json","r") as d:
#     directories=json.load(d)['directories']
    
# try:  
#     for k,v in directories.items():
#         dir_name=os.path.abspath("../"+v)
#         if not os.path.exists(dir_name):
#             try:
#                 os.mkdir(dir_name)
#             except:
#                 os.makedirs(dir_name)
# except:
#     pass



class Config(object) :
    if params['local_server']:
        if not database_exists(params['local_url']):
            create_database(params['local_url'])
    
        SQLALCHEMY_DATABASE_URI=params['local_url']
    else:
        if not database_exists(params['prod_url']):
            create_database(params['prod_url'])
        SQLALCHEMY_DATABASE_URI=params['prod_url']
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False

