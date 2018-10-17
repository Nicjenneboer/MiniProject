import sqlite3
import hashlib
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

def create_users(auth):
    naam = input("Naam: ")
    ww = hashlib.sha256(input("Wachtwoord: ").encode()).hexdigest()
    cur.execute('SELECT * FROM Users')
    for i in cur:
        if naam == i[0]:
            print ("Naam bestaad al!")
            exit()
    record = (naam, ww, auth)
    cur.execute("INSERT INTO Users VALUES (?, ?, ?)", record)
    con.commit()



def inloggen():
    global naam
    naam = input("Naam: ")
    ww = input("Wachtwoord: ")
    wrong = False
    cur.execute('SELECT * FROM Users')
    for i in cur:
        if naam == i[0]:
            cur.execute("SELECT wachtwoord FROM Users WHERE naam = ?", (naam,))
            if (cur.fetchall()[0][0]) == hashlib.sha256(ww.encode()).hexdigest():
                cur.execute("SELECT auth FROM Users WHERE naam = ?", (naam,))
                if cur.fetchall()[0][0] == 0:
                    gebruiker()
                else:
                    aanbieder()
                wrong = False
            else:
                wrong = True
        else:
            wrong = True
    if wrong == True:
        print ("Verkeerde gegevens!")

def aanbieder():
    print("Welkom aanbieder!")
    print("\n")
    menu = int(input("1. Beschibare films om aan te bieden.\n2. Mijn Films\n\n>>"))
    if menu == 1:
        print("Films Beschikbaar om aan te bieden:\n\n")
        cur.execute('SELECT titel FROM Films WHERE aanbieder = "0"')
        number = 0
        titels = cur.fetchall()
        for titel in titels:
            number += 1
            print("{}. {} ".format(number, titel[0]))
        q = int(input("Welke Film wil je zelf aanbieden?: "))
        print (titels[q - 1][0])
        cur.execute('UPDATE Films SET aanbieder = ? WHERE titel = ?', (naam, titels[q - 1][0]))
        con.commit()
    elif menu == 2:
        cur.execute('SELECT titel FROM Films WHERE aanbieder = ?', (naam,))
        for titels in cur.fetchall():
            print(titels[0])
def gebruiker():
    print("Welkom aanbieder!")
    print("\n")
    menu = int(input("1. Beschibare films om te bekijken.\n2. Mijn Films\n\n>>"))
    if menu == 1:
        cur.execute('SELECT titel FROM Films WHERE NOT aanbieder = "0"')
        for titels in cur.fetchall():
            print(titels[0])

con = sqlite3.connect('film.db')
cur = con.cursor()

api_ophalen(0)
api_ophalen(1)


x = int(input("1. Inloggen\n2. Account aanmaken\n3. Stoppen\n\n>> "))
if x == 1:
    inloggen()
elif x == 2:
    auth = int(input("0. Gebruikers account\n1. Aanbieders account\n\n>> "))
    create_users(auth)
else:
    exit()


con.close()