import requests
import datetime
import xml.etree.ElementTree as ET
import xmltodict
import sqlite3

def api_ophalen(dag):
    # dag = 0: Vandaag
    # dag = 1: Morgen
    key = "z9rqxl4qlkw14ozm3z5721oscmu88zoz"
    datenow = datetime.datetime.now()
    if dag == 0:
        date = datenow.strftime("%d-%m-%Y")
    elif dag == 1:
        date = str(int(datenow.strftime("%d")) + 1) + datenow.strftime("-%m-%Y")
    sorteer = "0"
    api_url = 'http://api.filmtotaal.nl/filmsoptv.xml?apikey=' + key + '&dag=' + date + '&sorteer=' + sorteer
    return requests.get(api_url)

def api_gegevens(gegeven):
    gegevens = xmltodict.parse(api_ophalen(0).text)
    vraag = []
    for i in gegevens["filmsoptv"]["film"]:
        vraag += [i[gegeven]]
    return vraag


print (api_gegevens("jaar"))
