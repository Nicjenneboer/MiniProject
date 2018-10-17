import sqlite3
con = sqlite3.connect('film.db')
cur = con.cursor()
import hashlib

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
                    print("Welkom gebruiker!")
                else:
                    print("Welkom aanbieder!")
                wrong = False
            else:
                wrong = True
        else:
            wrong = True
    if wrong == True:
        print ("Verkeerde gegevens!")




while True:
    x = int(input("1. Inloggen\n2. Account aanmaken\n3. Stoppen\n\n>> "))
    if x == 1:
        inloggen()
    elif x == 2:
        auth = int(input("0. Gebruikers account\n1. Aanbieders account\n\n>> "))
        create_users(auth)
    else:
        exit()
con.close()