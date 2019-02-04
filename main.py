# -*- coding: utf-8 -*-
import requests
import re
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


def run():       
    
    html = ''
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
    
    # search total of pages
    soup   =  BeautifulSoup(html, 'html.parser')
    elem   =  soup.find('div', {
        'class': 'pagination pagination text-center'
    }).find('ul').findAll('li')[-1].find('a')
    # parse num of pages
    r = re.compile("_materia_WAR_atividadeportlet_p=")
    data = elem["href"].split("&")
    num_pages =  str(filter(r.match, data)[0].split("=")[1])
        
    results = []    
    for i in range(int(num_pages)):       
        try:
            html = utils.request_page(i)
            soup = BeautifulSoup(html, 'html.parser') 
            table =  soup.find('div', {'class': 'div-zebra'})    
            divs  =  table.findAll('div')  
            info = []        
            for data in divs:               
                info = data.find('dl').findAll('dd')               
                obj = {}
                obj["materia"] = info[0].find('a').find("span").text.encode("utf-8")
                obj["link"] = info[0].find('a')["href"]
                obj["ementa"] = info[1].text.encode("utf-8")
                obj["autor"] = info[2].text.encode("utf-8")
                obj["data"]  = info[3].text.encode("utf-8")
                print("{} - {}".format(str(i+1),obj))
                results.append(obj)
        except:            
            print('error processing page: {} -- {}'.format(str(i), str(e)))
            continue    

    
if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print('error processing -- {}'.format(str(e)))
