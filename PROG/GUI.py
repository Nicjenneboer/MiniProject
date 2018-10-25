from tkinter import *
import sqlite3
import requests
import datetime
import xmltodict
import hashlib
from urllib.request import urlopen
from PIL import Image, ImageTk
import io


#API TO DATABASE FUNCITES
def api_ophalen(dag):
    global date
    key = "z9rqxl4qlkw14ozm3z5721oscmu88zoz"
    datenow = datetime.datetime.now()
    if dag == 0:
        date = datenow.strftime("%d-%m-%Y")
    elif dag == 1:
        date = str(int(datenow.strftime("%d")) + 1) + datenow.strftime("-%m-%Y")
    api_url = 'http://api.filmtotaal.nl/filmsoptv.xml?apikey=' + key + '&dag=' + date + '&sorteer=0'
    response = requests.get(api_url)
    return response

def api_ophalen_check():
    if str(api_ophalen(0)) and str(api_ophalen(1)) == "<Response [200]>":
        api_to_database()
        print("Goed")
    else:
        print ("Error")

def api_to_database():
    datenow = datetime.datetime.now()
    cur.execute('SELECT titel FROM Films')
    titels = cur.fetchall()
    columns = ['titel', 'jaar', 'regisseur', 'cast', 'genre', 'land', 'cover', 'duur', 'synopsis', 'imdb_rating', 'starttijd', 'eindtijd', 'filmtip']
    field = []
    for dag in range(2):
        gegevens = xmltodict.parse(api_ophalen(dag).text)
        for i in range(len(gegevens["filmsoptv"]["film"])):
            for column in columns:
                field += [(gegevens["filmsoptv"]["film"][i][column])]
            field += ['0'] + [date]
            if ((field[0],) not in titels):
                cur.execute("INSERT INTO Films VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", field)
                con.commit()
            field = []
    yesterday = str(int(datenow.strftime("%d")) - 1) + datenow.strftime("-%m-%Y")
    cur.execute('DELETE FROM Films WHERE datum=?', (yesterday,))
    cur.execute('DELETE FROM Tickets WHERE datum=?', (yesterday,))
    con.commit()



#toon Frames Functies


def toonLoginFrame():
    gebruikerhoofdframe.pack_forget()
    aanbiederhoofdframe.pack_forget()
    registerframe.pack_forget()
    loginframe.pack()
    Loginscreen()

def toonGebruikerHoofdFrame():
    aanbiederhoofdframe.pack_forget()
    loginframe.pack_forget()
    registerframe.pack_forget()
    gebruikerhoofdframe.pack()

def toonAanbiederHoofdFrame():
    loginframe.pack_forget()
    gebruikerhoofdframe.pack_forget()
    registerframe.pack_forget()
    aanbiederhoofdframe.pack()

def toonRegisterFrame():
    loginframe.pack_forget()
    gebruikerhoofdframe.pack_forget()
    aanbiederhoofdframe.pack_forget()
    registerframe.pack()
    Registerscreen()

#Button click functies


def login_clicked(usern, userp):
    global username
    username = userp
    userpass = usern
    wrong = False
    cur.execute('SELECT * FROM Users')
    for i in cur:
        if username == i[0]:
            cur.execute("SELECT wachtwoord FROM Users WHERE naam = ?", (username,))
            if (cur.fetchall()[0][0]) == hashlib.sha256(userpass.encode()).hexdigest():
                cur.execute("SELECT auth FROM Users WHERE naam = ?", (username,))
                if cur.fetchall()[0][0] == 0:
                    gebruiker_login()
                else:
                    aanbieder_login()
                wrong = False
            else:
                wrong = True
        else:
            wrong = True
    if wrong == True:
        wrong_input_login.config(text='Verkeerde gegevens!')



def registreer_clicked(auth, usern, userp, userpc):
    naam = usern
    autho = auth
    ww = hashlib.sha256(userp.encode()).hexdigest()
    if userp == userpc:
        cur.execute('SELECT * FROM Users')
        for i in cur:
            if naam == i[0]:
                print ("Naam bestaad al!")
                exit()
        record = (naam, ww, autho)
        print (record)
        cur.execute("INSERT INTO Users VALUES (?, ?, ?)", record)
        con.commit()
        toonLoginFrame()
    else:
        print ("Fout")

#GUI FRAMES


def Loginscreen():
    global wrong_input_login
    BACKGROUND(loginframe, 'img/background.png')
    username_entry = Entry(master=loginframe, width=25, font=('Verdana', 15))
    userpass_entry = Entry(master=loginframe, width=25, font=('Verdana', 15), show="*")
    username_label = Label(master=loginframe, text="Gebruikersnaam:", font=('Verdana', 15))
    userpass_label = Label(master=loginframe, text="Wachtwoord:", font=('Verdana', 15))
    login_button = Button(master=loginframe, text="Login!",command=lambda: login_clicked(username_entry.get(), userpass_entry.get()),font=('Verdana', 20), activebackground="#b00000", background="#d00000", bd=0, fg="#fff")
    registreerframe_button = Button(master=loginframe, text="Maak een account aan.", command=lambda: toonRegisterFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    wrong_input_login = Label(master=loginframe, text="", font=('Verdana', 15))
    # Place
    username_label.place(relx=0.3, rely=0.58, anchor=CENTER)
    userpass_label.place(relx=0.3, rely=0.63, anchor=CENTER)
    username_entry.place(relx=0.5, rely=0.58, anchor=CENTER)
    userpass_entry.place(relx=0.5, rely=0.63, anchor=CENTER)
    login_button.place(relx=0.68, rely=0.605, anchor=CENTER)
    registreerframe_button.place(relx=0.85, rely=0.05, anchor=CENTER)
    wrong_input_login.place(relx=0.5, rely=0.53, anchor=CENTER)




def Registerscreen():
    BACKGROUND(registerframe, 'img/background.png')
    v = IntVar()
    aanbieder = Radiobutton(registerframe, text="Aanbieder", variable=v, value=1)
    gebruiker = Radiobutton(registerframe, text="Gebruiker", variable=v, value=0)
    gebruiker.invoke()
    username_entry = Entry(master=registerframe, width=25, font=('Verdana', 15))
    userpass_entry = Entry(master=registerframe, width=25, font=('Verdana', 15), show="*")
    userpasscheck_entry = Entry(master=registerframe, width=25, font=('Verdana', 15), show="*")
    username_label = Label(master=registerframe, text="Gebruikersnaam:", font=('Verdana', 15))
    userpass_label = Label(master=registerframe, text="Wachtwoord:", font=('Verdana', 15))
    userpasscheck_label = Label(master=registerframe, text="Wachtwoord verifieren:", font=('Verdana', 15))
    registreer_button = Button(master=registerframe, text="Registreer!",command=lambda: registreer_clicked(str(v.get()), username_entry.get(), userpass_entry.get(), userpasscheck_entry.get()),font=('Verdana', 20), activebackground="#b00000", background="#d00000", bd=0, fg="#fff")
    loginframe_button = Button(master=registerframe, text="Login",command=lambda: toonLoginFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    # Place
    aanbieder.place(relx=0.55, rely=0.54, anchor=CENTER)
    gebruiker.place(relx=0.46, rely=0.54, anchor=CENTER)
    username_label.place(relx=0.335, rely=0.58, anchor=CENTER)
    userpass_label.place(relx=0.35, rely=0.63, anchor=CENTER)
    userpasscheck_label.place(relx=0.31, rely=0.68, anchor=CENTER)
    username_entry.place(relx=0.55, rely=0.58, anchor=CENTER)
    userpass_entry.place(relx=0.55, rely=0.63, anchor=CENTER)
    userpasscheck_entry.place(relx=0.55, rely=0.68, anchor=CENTER)
    registreer_button.place(relx=0.61, rely=0.75, anchor=CENTER)
    loginframe_button.place(relx=0.94, rely=0.05, anchor=CENTER)

def gebruiker_login():
    toonGebruikerHoofdFrame()
    login_succes_welkom_label = Label(master=gebruikerhoofdframe, text="Welkom gebruiker!")
    login_succes_welkom_label.pack(pady=10)
    b = Button(master=gebruikerhoofdframe, command=lambda: toonLoginFrame(), width=12, height=12)
    b.pack(pady=10)

def sjaak(p):
    global tk_img
    global tk_img2
    global tk_img3
    global x
    if p == 1:
        x = x + 1
    else:
        x = x - 1
    print (x)
    for i in range(3):
        url = (list[i + x])
        print (list[i + x])
        my_page = urlopen(url)
        my_picture = io.BytesIO(my_page.read())
        pil_img = Image.open(my_picture)
        if i == 0:
            tk_img = ImageTk.PhotoImage(pil_img)
            label = Button(master=aanbiederhoofdframe, image=tk_img)
            label.place(relx=0.2, rely=0.5, anchor=CENTER)
        elif i == 1:
            tk_img2 = ImageTk.PhotoImage(pil_img)
            label2 = Button(master=aanbiederhoofdframe, image=tk_img2)
            label2.place(relx=0.5, rely=0.5, anchor=CENTER)
        elif i == 2:
            tk_img3 = ImageTk.PhotoImage(pil_img)
            label3 = Button(master=aanbiederhoofdframe, image=tk_img3)
            label3.place(relx=0.8, rely=0.5, anchor=CENTER)

def aanbieder_login():
    global tk_img
    global tk_img2
    global tk_img3
    global list
    global x
    BACKGROUND(aanbiederhoofdframe, 'img/background.png')
    toonAanbiederHoofdFrame()
    cur.execute('SELECT cover FROM Films WHERE aanbieder = "0"')
    titels = cur.fetchall()
    list = []
    for titel in titels:
        list += [str(titel[0])]
    print(list)
    x = 0
    sjaak(1)
    b = Button(master=aanbiederhoofdframe, command=lambda: sjaak(2), width=5, height=5, text="<")
    b.place(relx=0.05, rely=0.5, anchor=CENTER)
    c = Button(master=aanbiederhoofdframe, command=lambda: sjaak(1), width=5, height=5, text=">")
    c.place(relx=0.95, rely=0.5, anchor=CENTER)


def BACKGROUND(frame, img):
    global filename
    background = Canvas(master=frame, height=750, width=1300)
    filename = PhotoImage(file=img)
    background_label = Label(master=frame, image=filename)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background.pack()


con = sqlite3.connect('film.db')
cur = con.cursor()
display_x = "1300"
display_y = "750"

api_ophalen_check()



#GUI
root = Tk()

#Root Settings
root.title("Thuis Bioscoop")
root.geometry("{}x{}".format(display_x, display_y))
root.resizable(False, False)




#Frames
loginframe = Frame(master=root)
gebruikerhoofdframe = Frame(master=root)
aanbiederhoofdframe = Frame(master=root)
registerframe = Frame(master=root)





Loginscreen()
toonLoginFrame()


root.mainloop()

con.close()



