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
    response = requests.get(api_url)
    cur.execute('SELECT titel FROM Films')
    titels = cur.fetchall()
    columns = ['titel', 'jaar', 'regisseur', 'cast', 'genre', 'land', 'cover', 'duur', 'synopsis', 'imdb_rating', 'starttijd', 'eindtijd', 'filmtip']
    gegevens = xmltodict.parse(response.text)
    field = []
    for i in range(len(gegevens["filmsoptv"]["film"])):
        for column in columns:
            field += [(gegevens["filmsoptv"]["film"][i][column])]
        field += ['0'] + [date]
        if ((field[0],) not in titels):
            cur.execute("INSERT INTO Films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", field)
            con.commit()
        field = []


con = sqlite3.connect('film.db')
cur = con.cursor()
api_ophalen(0)
api_ophalen(1)
con.close()
