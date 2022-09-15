# https://softhints.com/python-read-validate-and-import-csv-json-file-to-mysql/
import pymysql
import json
from SQLHelper import *
import requests
from os.path import exists



def setupDB(data_url,file,dbName):
    getJsonFile(data_url,file)
    json_obj=getJsonObj(file)
    setJson2MySQL(json_obj,dbName)

def getJsonFile(data_url,file):
    if not exists(file):
        req = requests.get(data_url).content
        with open(file, 'wb') as handler:
            handler.write(req)

def getJsonObj(file):
    # read JSON file which is in the next parent folder    
    json_data = open(file).read()
    json_obj = json.loads(json_data)
    return json_obj

# do validation and checks before insert
def validate_string(val):
    if val != None:
        if type(val) is int:
            # for x in val:
            #   print(x)
            return str(val).encode('utf-8')
        else:
            return val

def setJson2MySQL(json_obj,dbName):
    # connect to MySQL
    #dbName = 'MTG_FULL4'
    connection = create_server_connection('localhost', 'mal', 'sql')
    remove_database(connection, dbName)
    dbExists = dbExist(connection, dbName)
    newCols = '(name text, manacost text, manavalue text, loyalty text, types text, subtypes text, text text, multiverseId text, availability text, side text)'
    autoCommit(connection, 'ON')
    if not dbExists:
        create_database(connection, dbName)
    createTable(connection, dbName, 'cards', newCols)
    paramsToKeep = newCols.replace(' text,', ',').replace(' text)', '')\
        .replace('(', '').replace(')', '').replace(' ', '').split(',')
    autoCommit(connection, 'OFF')
    con = pymysql.connect(host='localhost', user='mal', passwd='sql', db=dbName)
    cursor = con.cursor()

    # parse json data to SQL insert
    data = json_obj.get("data", None)
    myid = 0
    if isinstance(data, dict):
        for setName, setInfo in data.items():
            setCards = setInfo.get("cards", None)
            if isinstance(setCards, list):
                for card in setCards:
                    if isinstance(card, dict):
                        stringNames = ''
                        cardVals = []
                        types = ''
                        ids = card.get("identifiers", None)
                        for param, val in ids.items():
                            # param = p.lower()
                            if param in paramsToKeep:
                                stringNames = param
                                cardVals = [str(val)]
                                types = '%s'
                        if len(cardVals) == 0:
                            stringNames = 'multiverseId'
                            cardVals = ['0']
                            types = '%s'
                        for p, val in card.items():
                            param = p.lower()
                            if param in paramsToKeep:
                                stringNames = stringNames + ', ' + param
                                cardVals = cardVals + \
                                        [str(val).replace('[\'', '').replace('\']', '').replace('\', \'', ' ')]
                                types = types + ', %s'
                    vals = tuple(cardVals)
                    cursor.execute('INSERT INTO cards (' + stringNames + ') VALUES (' + types + ')', vals)
    con.commit()
    con.close()

if __name__ == '__main__':
    data_url = 'https://mtgjson.com/api/v5/AllPrintings.json'
    file = '/media/VMShare/AllPrintings20220823.json'
    dbName = 'MTG_FULL4'
    setupDB(data_url,file,dbName)
