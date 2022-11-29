
import os
from addict import Dict as AttrDict
import json
import datetime
import requests
import traceback
import pandas as pd




CurrentDirectory = os.path.join(os.path.dirname(os.path.realpath(__file__)))
now = datetime.datetime.now()


try:
    with open(CurrentDirectory+'/confg.json','r') as confg_file:
        confg = json.load(confg_file)
        confg_file.close()
    confg = AttrDict(confg)
    if confg.agol.is_public is False:
        if os.path.exists('token.json'):
            timestampNow = int(datetime.datetime.timestamp(now)*1000)
            with open('token.json') as tk:
                tokenData = json.load(tk)
                tk.close()
            validTill = tokenData['expires']
            if validTill > timestampNow:
                token = tokenData['token']
            else:
                tokenURL = 'https://www.arcgis.com/sharing/rest/generatetoken'
                params = {'f': 'json',
                'username': confg.agol.username,
                'password': confg.agol.password,
                'referer': 'https://www.arcgis.com'}
                response = requests.post(tokenURL, data=params)
                responseJson = response.json()
                with open('token.json','w') as tk:
                    json.dump(responseJson, tk)
                    tk.close()
                token = response.json()['token']
        else:
            tokenURL = 'https://www.arcgis.com/sharing/rest/generateToken' 
            params = {'f': 'json', 
            'username': confg.agol.username,
            'password': confg.agol.password, 
            'referer': 'https://ww.arcgis.com'}
            response = requests .post (tokenURL, data = params) 
            responseJson = response.json()
            with open('token.json', 'w') as tk:
                json.dump(responseJson, tk) 
                tk.close()
            token = response.json()['token' ]
    else:
        token='' 
        print('token not required')    
            
    agolURL = confg.agol.URL
    
    response = requests.get("{}/{}?f=json&token={}".format(agolURL,"arcgis/rest/services",token))
    
    
    service_details=[]
    allServices = response.json()['services']
    for service in allServices:
        if service['type'] != 'FeatureServer':
            print('Skipping service {}'.format(service['type']))
        else:

            response = requests.get("{}/{}/{}/{}?f=json&token={}".format(agolURL,"arcgis/rest/services",service['name'],service['type'],token))
            responseJson = response.json()
            
            if len(responseJson["layers"])>0:
                layername = []
                for layer in responseJson["layers"]:
                    layername.append(layer['name'])
                layerInfo = "{} ({})".format(len(responseJson["layers"]),','.join(layername))
            else:
                layerInfo = "{}".format(len(responseJson["layers"]))

            if len(responseJson["tables"])>0:
                tablename = []
                for table in responseJson["tables"]:
                    tablename.append(table['name'])
                tableInfo = "{} ({})".format(len(responseJson["tables"]),','.join(tablename))
            else:
                tableInfo = "{}".format(len(responseJson["tables"]))
            

            service_details.append({'Serivce Name': service['name'],'Serivce Description': responseJson["serviceDescription"],'Maximum Records Count':responseJson['maxRecordCount'],  'Units':responseJson["units"] , 'Enabled Capabilities':responseJson["capabilities"] , 'Layers':layerInfo, 'Tables':tableInfo })
    print(service_details)

    df = pd.DataFrame.from_dict(service_details)
    df.to_html('ServicesOverview.html',index=False)



except Exception as e:
    print(e)
    print(traceback.format_exc())

