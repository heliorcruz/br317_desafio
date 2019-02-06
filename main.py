# -*- coding: utf-8 -*-
import requests
import re
import pymongo
import configparser
from bs4 import BeautifulSoup
import config as constants

class Utils:
    
    def __init__(self):
        self.config = {}        
        self.connection = {}
        
    def load_config(self):
        '''
           config.ini [initial configuration]
           config.py [constants file]
        '''
        self.config = configparser.ConfigParser()        
        self.config.read('config.ini')
        self.constants = constants
        
    def get_config(self):
       
        params = 'data'       
        search = self.config["DEFAULT"]
        for v in search.values():
            params += '_{}'.format(v) if v is not None else ''
        return params             
       
        
    def request_page(self, page):
        '''
            request html by page number
            @return response text
        '''
        p = self.constants
        params = p.PARAMS
        items  = p.FILTER.items()
        search = self.config["DEFAULT"]
        for k,v in items:
            params += '&{}={}'.format(v,search[k])
        params += '&{}={}'.format(p.PAGES, page)        
        response = requests.get(p.URL + params)
        if response.status_code == 200:
            return response.text
        else:
            raise ValueError(str(response.status_code))
        
    def connect_database(self):
        db_conf = self.config["DATABASE"]
        conn_str = 'mongodb://{0}:{1}@{2}:{3}/{4}'.format(db_conf["user"],
                                                          db_conf["password"],
                                                          db_conf["host"],
                                                          db_conf["port"],
                                                          db_conf["dbname"])
        dbCon = pymongo.MongoClient(conn_str)
        return dbCon[db_conf["dbname"]]    


def run():       
    
    html = ''
    db   = {}
    utils = Utils()
    
    try:
        utils.load_config()
    except Exception as e:
        print('error loading configuration: {}'.format(str(e)))
        return
    
    try:        
        html = utils.request_page(1)
    except Exception as e:
        print('error on first request: {}'.format(str(e)))
        return
    
    try:        
        db = utils.connect_database()
    except Exception as e:
        print('error on db connection {}'.format(str(e)))
        return
    
    # search total of pages
    soup   =  BeautifulSoup(html, 'html.parser')
    # check data not available
    not_avail = soup.find('div', {'class':constants.NOT_AVAILABLE[0]})
    not_avail = not_avail.find('div', {'class': constants.NOT_AVAILABLE[1]})
    not_avail = not_avail.text.strip(' ') if not_avail is not None else ''
    if not_avail == constants.NOT_AVAILABLE[2]:
        print('error: data is not available')
        return
        
    
    elem   =  soup.find('div', {
        'class': constants.PAGINATION
    }).find('ul').findAll('li')[-1].find('a')
    # parse num of pages
    r = re.compile(constants.PAGES + '=')
    data = elem["href"].split("&")
    num_pages =  str(filter(r.match, data)[0].split("=")[1])
        
    results = []    
    for i in range(int(num_pages)):       
        try:
            html = utils.request_page(i)
            soup = BeautifulSoup(html, 'html.parser') 
            table =  soup.find('div', {'class': constants.TABLE_DIV})    
            divs  =  table.findAll('div')  
            info = []        
            for data in divs:               
                info = data.find('dl').findAll('dd')               
                obj = {}
                obj["materia"] = info[0].find('a').find("span").text
                obj["link"] = info[0].find('a')["href"]
                obj["ementa"] = info[1].text.encode("utf-8")
                obj["autor"] = info[2].text.encode("utf-8")
                obj["data"]  = info[3].text.encode("utf-8")
                print("{} - {}".format(str(i+1),obj))
                results.append(obj)
        except:            
            print('error processing page: {} -- {}'.format(str(i), str(e)))
            continue 
        
    try:
        collection = utils.get_config()
        db[collection].update_many( results ,{'$set': results },upsert=True)
    except Exception as e:
        print('error inserting data: {}'.format(str(e)))  

    
if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print('error processing -- {}'.format(str(e)))
