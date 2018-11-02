from tkinter import *
import sqlite3
import requests
import datetime
import xmltodict
import hashlib
from urllib.request import urlopen
from PIL import Image, ImageTk
import io
from tkinter.messagebox import showinfo
import time
from datetime import timedelta
import pyqrcode

# API TO DATABASE FUNCITES
def api_ophalen(dag):
    global date
    key = "z9rqxl4qlkw14ozm3z5721oscmu88zoz"
    datenow = datetime.datetime.now()
    if dag == 0:
        date = datenow.strftime("%d-%m-%Y")
    elif dag == 1:
        datenow2 = datetime.datetime.now() + timedelta(days=1)
        date = datenow2.strftime("%d-%m-%Y")
    api_url ='http://api.filmtotaal.nl/filmsoptv.xml?apikey=' + key + '&dag=' + date + '&sorteer=0'
    response = requests.get(api_url)
    return response

# Geeft weer of de api opgehaalt kan worden.
def api_ophalen_check():
    if str(api_ophalen(0)) and str(api_ophalen(1)) == "<Response [200]>":
        api_to_database()
    else:
        print("Error")

# Geeft weer of er wel of geen internet is om het om de GUI te openen .
def internet_check():
    while True:
        try:
            api_ophalen_check()
            break
        except:
            print("geen internet")
            time.sleep(5)

# API gegevens naar database sorteren
def api_to_database():
    datenow = datetime.datetime.now()
    cur.execute('SELECT titel FROM Films')
    titels = cur.fetchall()
    columns = ['titel', 'jaar', 'regisseur', 'cast', 'genre', 'land', 'cover', 'duur', 'synopsis', 'imdb_rating',
             'starttijd', 'eindtijd', 'filmtip']
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
    yesterday = datetime.datetime.now() + timedelta(days=-1)
    cur.execute('DELETE FROM Films WHERE datum=?', (yesterday.strftime("%d-%m-%Y"),))
    cur.execute('DELETE FROM Tickets WHERE datum=?', (yesterday.strftime("%d-%m-%Y"),))
    con.commit()


# toon Frames Functies
def toonFilmsGebruikersFrame():
    loginframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    filmaanbiedenframe.pack_forget()
    filmsaanbiederframe.pack_forget()
    filmgebruikenframe.pack_forget()
    mijnfilmsgebruikerframe.pack_forget()
    filmsgebruikerframe.pack()
    Filmsgebruikerscreen()

def toonFilmGebruikenFrame(cover):
    filmgebruikenframe.pack()
    filmsgebruikerframe.pack_forget()
    Filmgebruikenscreen(cover)

def toonFilmsAanbiederFrame():
    loginframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    filmaanbiedenframe.pack_forget()
    filmsaanbiederframe.pack()
    Filmsaanbiederscreen()


def toonFilmAanbiedenFrame(cover):
    loginframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    filmsaanbiederframe.pack_forget()
    filmaanbiedenframe.pack()
    Filmaanbiedenscreen(cover)


def toonMijnFilmAanbiedenFrame(cover):
    loginframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    filmsgebruikerframe.pack_forget()
    filmsaanbiederframe.pack_forget()
    filmaanbiedenframe.pack_forget()
    mijnfilmaanbiedenframe.pack()
    Mijnfilmaanbiedenscreen(cover)



def toonMijnFilmGebruikenFrame(cover):
    mijnfilmsgebruikerframe.pack_forget()
    mijnfilmgebruikenframe.pack()
    Mijnfilmgebruikenscreen(cover)


def toonMijnFilmsGebruikersFrame():
    loginframe.pack_forget()
    filmsgebruikerframe.pack_forget()
    mijnfilmgebruikenframe.pack_forget()
    mijnfilmsgebruikerframe.pack()
    Mijnfilmsgebruikerscreen()


def toonMijnFilmsAanbiederFrame():
    filmsaanbiederframe.pack_forget()
    mijnfilmaanbiedenframe.pack_forget()
    mijnfilmsaanbiederframe.pack()
    Mijnfilmsaanbiederscreen()


def toonLoginFrame():
    filmaanbiedenframe.pack_forget()
    registerframe.pack_forget()
    filmsaanbiederframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    filmsgebruikerframe.pack_forget()
    mijnfilmaanbiedenframe.pack_forget()
    filmgebruikenframe.pack_forget()
    mijnfilmgebruikenframe.pack_forget()
    mijnfilmsgebruikerframe.pack_forget()
    loginframe.pack()
    Loginscreen()


def toonRegisterFrame():
    loginframe.pack_forget()
    registerframe.pack()
    Registerscreen()


# Button click functies
# Ook de popups: voor als de informatie niet goed wordt ingevuld


def login_clicked(usern, userp):
    global username
    username = userp
    userpass = usern
    wrong = False
    if username and userpass == "":
        popup("Vul iets in")
    else:
        cur.execute('SELECT * FROM Users')
        for i in cur:
            if username == i[0]:
                cur.execute("SELECT wachtwoord FROM Users WHERE naam = ?", (username,))
                if (cur.fetchall()[0][0]) == hashlib.sha256(userpass.encode()).hexdigest():
                    cur.execute("SELECT auth FROM Users WHERE naam = ?", (username,))
                    if cur.fetchall()[0][0] == 0:
                        toonFilmsGebruikersFrame()
                    else:
                        cur.fetchall()
                        toonFilmsAanbiederFrame()
                    wrong=False
                else:
                    wrong=True
            else:
                wrong=True
        if wrong == True:
            popup('Verkeerde inlog gegevens!')

# Accounts aanmaken voor gebruiker en aanbieder.(via buttons)

def registreer_clicked(auth, usern, userp, userpc):
    gebruikersnaambestaatniet = False
    naam = usern
    autho = auth
    ww = hashlib.sha256(userp.encode()).hexdigest()
    if userp == userpc:
        cur.execute('SELECT * FROM Users')
        for i in cur:
            if naam == i[0]:
                gebruikersnaambestaatniet=False
                break
            else:
                gebruikersnaambestaatniet=True
        if gebruikersnaambestaatniet == True:
            record=(naam, ww, autho)
            cur.execute("INSERT INTO Users VALUES (?, ?, ?)", record)
            con.commit()
            if autho == '0':
                popup('Gebruikers account aangemaakt!')
            elif autho == '1':
                popup('Aanbieders account aangemaakt!')
            toonLoginFrame()
        elif gebruikersnaambestaatniet == False:
            popup('Gebruikersnaam bestaat al')
    else:
        popup('Wachtwoord komt niet overheen')



def film_aanbieden_clicked(titel):
    cur.execute('UPDATE Films SET aanbieder = ? WHERE titel = ?', (username, titel))
    con.commit()
    popup('Je biedt nu de film: {}. aan en is te vinden bij mijn films'.format(titel))
    toonFilmsAanbiederFrame()

def film_ticket_kopen_clicked(titel):
    cur.execute('SELECT datum FROM Films WHERE titel = ?', (titel,))
    datum = cur.fetchall()[0][0]
    code = hashlib.sha256((username + titel).encode()).hexdigest()
    cur.execute('INSERT INTO Tickets VALUES (?, ?, ?, ?)', (username, titel, code, datum))
    con.commit()
    popup('Je hebt een ticket gekocht voor de film: {}! Bekijk je ticket bij joun films.'.format(titel))
    toonFilmsGebruikersFrame()


# popup
def popup(bericht):
    showinfo(title='HomeScoop', message=bericht)

# Op het login frame, samen met buttons en labels
def Loginscreen():
    global wrong_input_login
    BACKGROUND(loginframe, 'img/loginbackground.png')
    username_entry = Entry(master=loginframe, width=25, font=('Verdana', 15))
    userpass_entry = Entry(master=loginframe, width=25, font=('Verdana', 15), show="*")
    username_label = Label(master=loginframe, text="Gebruikersnaam:", font=('Verdana', 15))
    userpass_label = Label(master=loginframe, text="Wachtwoord:", font=('Verdana', 15))
    login_button = Button(master=loginframe, text="Login",
                        command=lambda: login_clicked(username_entry.get(), userpass_entry.get()), font=('Verdana', 20),
                        activebackground="#b00000", background="#d00000", bd=0, fg="#fff")
    registreerframe_button = Button(master=loginframe, text="Maak hier een account aan", command=lambda: toonRegisterFrame(),
                                  font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0,
                                  fg="#b00000", border=0)
    exit_button = Button(master=loginframe, text="Exit",
                                    command=lambda: exit(),
                                    font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0,
                                    fg="#b00000", border=0)
    # Plek
    username_label.place(relx=0.3, rely=0.58, anchor=CENTER)
    userpass_label.place(relx=0.315, rely=0.63, anchor=CENTER)
    username_entry.place(relx=0.52, rely=0.58, anchor=CENTER)
    userpass_entry.place(relx=0.52, rely=0.63, anchor=CENTER)
    login_button.place(relx=0.70, rely=0.605, anchor=CENTER)
    registreerframe_button.place(relx=0.84, rely=0.05, anchor=CENTER)
    exit_button.place(relx=0.04, rely=0.95, anchor=CENTER)

# Geeft films weer. verschillend van de gebruiker en de aanbieder.
def filmscreencheck(cover):
    if filmscreencheckint == 1:
        toonFilmAanbiedenFrame(cover)
    elif filmscreencheckint == 2:
        toonMijnFilmAanbiedenFrame(cover)
    elif filmscreencheckint == 3:
        toonFilmGebruikenFrame(cover)
    elif filmscreencheckint == 4:
        toonMijnFilmGebruikenFrame(cover)

# Frame voor registratie van zowel gebruikers als aanbieders
def Registerscreen():
    BACKGROUND(registerframe, 'img/registreerbackground.png')
    v = IntVar()
    aanbieder = Radiobutton(registerframe, text="Aanbieder", variable=v, value=1, font=('Verdana', 12))
    gebruiker = Radiobutton(registerframe, text="Gebruiker", variable=v, value=0, font=('Verdana', 12))
    gebruiker.invoke()
    username_entry = Entry(master=registerframe, width=25, font=('Verdana', 15))
    userpass_entry = Entry(master=registerframe, width=25, font=('Verdana', 15), show="*")
    userpasscheck_entry = Entry(master=registerframe, width=25, font=('Verdana', 15), show="*")
    username_label = Label(master=registerframe, text="Gebruikersnaam:", font=('Verdana', 15))
    userpass_label = Label(master=registerframe, text="Wachtwoord:", font=('Verdana', 15))
    userpasscheck_label = Label(master=registerframe, text="Wachtwoord verifieren:", font=('Verdana', 15))
    registreer_button = Button(master=registerframe, text="Registreer",
                             command=lambda: registreer_clicked(str(v.get()), username_entry.get(),
                                                                userpass_entry.get(), userpasscheck_entry.get()),
                             font=('Verdana', 20), activebackground="#b00000", background="#d00000", bd=0, fg="#fff")
    loginframe_button=Button(master=registerframe, text="Login", command=lambda: toonLoginFrame(), font=('Verdana', 20),
                             activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000", border=0)
    # Plek
    aanbieder.place(relx=0.60, rely=0.528, anchor=CENTER)
    gebruiker.place(relx=0.51, rely=0.528, anchor=CENTER)
    username_label.place(relx=0.402, rely=0.58, anchor=CENTER)
    userpass_label.place(relx=0.419, rely=0.63, anchor=CENTER)
    userpasscheck_label.place(relx=0.38, rely=0.68, anchor=CENTER)
    username_entry.place(relx=0.6, rely=0.58, anchor=CENTER)
    userpass_entry.place(relx=0.6, rely=0.63, anchor=CENTER)
    userpasscheck_entry.place(relx=0.6, rely=0.68, anchor=CENTER)
    registreer_button.place(relx=0.61, rely=0.75, anchor=CENTER)
    loginframe_button.place(relx=0.94, rely=0.05, anchor=CENTER)

# Zet buttons voor de slides neer.
def img_slide(frame, user, auth):
    global count
    count = 0
    film_img_slide(0, frame, user, auth)
    next = Button(master=frame, text=">", command=lambda: film_img_slide(1, frame, user, auth))
    next.place(relx=0.92, rely=0.6, anchor=CENTER)
    back = Button(master=frame, text="<", command=lambda: film_img_slide(2, frame, user, auth))
    back.place(relx=0.08, rely=0.6, anchor=CENTER)

# Het doorklikken van films in de GUI. (slides
def film_img_slide(next, frame, user, auth):
    global tk_img1
    global tk_img2
    global tk_img3
    global tk_img4
    global count
    if next == 1:
        count += 1
    elif next == 0:
        count = 0
    elif next == 2:
        count -= 1
    cur.fetchall()
    filmimglist = []
    if auth == 3:
        cur.execute('SELECT Film FROM Tickets WHERE User = ?', (str(user),))
        titels = cur.fetchall()
        for titel in titels:
            cur.execute('SELECT cover FROM Films WHERE titel = ?', (titel[0],))
            cover = cur.fetchall()
            filmimglist += [cover[0][0]]
    elif auth == 0:
        cur.execute('SELECT titel FROM Films WHERE NOT aanbieder = 0')
        titels = cur.fetchall()
        cur.execute('SELECT Film FROM Tickets WHERE User = ?', (user,))
        btitels = list(set(titels) - set(cur.fetchall()))
        for titel in btitels:
            cur.execute('SELECT cover FROM Films WHERE titel = ?', (titel[0],))
            cover = cur.fetchall()
            filmimglist += [cover[0][0]]
    else:
        cur.execute('SELECT cover FROM Films WHERE aanbieder = ?', (str(user),))
        for cover in cur:
            filmimglist += [cover[0]]
    if count < 0:
        count = 0
    elif count > len(filmimglist) - 4:
        count = len(filmimglist) - 4
    if len(filmimglist) < 4:
        leng = len(filmimglist)
        count = 0
    else:
        leng=4
    show_image_slide(frame, count, filmimglist, leng)

# Foto's van de angeboden films
def show_image_slide(frame, count, filmimglist, leng):
    global tk_img1
    global tk_img2
    global tk_img3
    global tk_img4
    for i in range(leng):
        my_page = urlopen(filmimglist[i + count])
        my_picture = io.BytesIO(my_page.read())
        pil_img=Image.open(my_picture)
        if i == 0:
            tk_img1=ImageTk.PhotoImage(pil_img)
            film2 = Button(frame, image=tk_img1, command=lambda: filmscreencheck(filmimglist[0 + count]))
            film2.place(relx=0.2, rely=0.55, anchor=CENTER)
            slide(frame, filmimglist, i, 0.2)
        elif i == 1:
            tk_img2=ImageTk.PhotoImage(pil_img)
            film2=Button(frame, image=tk_img2, command=lambda: filmscreencheck(filmimglist[1 + count]))
            film2.place(relx=0.4, rely=0.55, anchor=CENTER)
            slide(frame, filmimglist, i, 0.4)
        elif i == 2:
            tk_img3=ImageTk.PhotoImage(pil_img)
            film3=Button(frame, image=tk_img3, command=lambda: filmscreencheck(filmimglist[2 + count]))
            film3.place(relx=0.6, rely=0.55, anchor=CENTER)
            slide(frame, filmimglist, i, 0.6)
        elif i == 3:
            tk_img4=ImageTk.PhotoImage(pil_img)
            film4=Button(frame, image=tk_img4, command=lambda: filmscreencheck(filmimglist[3 + count]))
            film4.place(relx=0.8, rely=0.55, anchor=CENTER)
            slide(frame, filmimglist, i, 0.8)

def slide(frame, filmimglist, i, x):
    cur.execute('SELECT starttijd FROM Films WHERE cover = ?', (filmimglist[i + count],))
    filmstartdate = datetime.datetime.utcfromtimestamp(cur.fetchall()[0][0]).strftime('%H:%M\n%m-%d')
    Label(frame, text=filmstartdate, background='#fff', font=('Verdana', 16)).place(relx=x, rely=0.86, anchor=CENTER)

def uitlog_button(frame):
    uitlog_button = Button(master=frame, text="Uitloggen", command=lambda: toonLoginFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    uitlog_button.place(relx=0.92, rely=0.05, anchor=CENTER)


# De foto van de gekozen film
def showcover(frame, url, x, y):
    global tk_img
    my_page = urlopen(url)
    my_picture = io.BytesIO(my_page.read())
    pil_img = Image.open(my_picture)
    tk_img = ImageTk.PhotoImage(pil_img)
    label = Label(frame, image=tk_img)
    label.place(relx=x, rely=y, anchor=CENTER)

# Beschrijving van de film
def showfilmdescription(frame, titel, x, y):
    cur.execute('SELECT synopsis FROM Films WHERE titel=?', (titel,))
    desc = cur.fetchall()[0][0]
    p = '\n'.join(desc[i:i + 120] for i in range(0, len(desc), 120))
    label = Label(master=frame, background='#fff', text=p, justify=LEFT)
    label.place(relx=x, rely=y, anchor=NW)

# Boordeling van de film
def showfilmdescriptionrate(frame, titel, x, y):
    cur.execute('SELECT imdb_rating FROM Films WHERE titel=?', (titel,))
    desc = cur.fetchall()[0][0]
    label = Label(master=frame, background='#fff', text=desc, justify=LEFT)
    label.place(relx=x, rely=y, anchor=NW)

def showfilmtitel(frame, titel, x, y):
    cur.execute('SELECT titel FROM Films WHERE titel=?', (titel,))
    desc = cur.fetchall()[0][0]
    label = Label(master=frame, background='#fff', text=desc, justify=LEFT, font=('Verdana', 16))
    label.place(relx=x, rely=y, anchor=NW)

def showfilmdatum(frame, cover, x, y):
    cur.execute('SELECT starttijd FROM Films WHERE cover = ?', (cover,))
    filmstartdate = datetime.datetime.utcfromtimestamp(cur.fetchall()[0][0]).strftime('%H:%M   %d-%m-%Y')
    Label(frame, text=filmstartdate, background='#fff', font=('Verdana', 16)).place(relx=x, rely=y, anchor=CENTER)
# Plaats frames, buttons en labels bij elkaar.
def Filmsaanbiederscreen():
    global filmscreencheckint
    filmscreencheckint = 1
    BACKGROUND(filmsaanbiederframe, 'img/films-a-background.png')
    films_button = Button(master=filmsaanbiederframe, text='Mijn Films', command=lambda: toonMijnFilmsAanbiederFrame(),
                        width=10, height=2, font=('Verdana', 14), activebackground="#ffcccc", background="#fff", bd=0,
                        fg="#b00000", border=0)
    films_button.place(relx=0.232, rely=0.24, anchor=CENTER)
    img_slide(filmsaanbiederframe, 0, 1)
    uitlog_button(filmsaanbiederframe)

# Plaats frames, buttons en labels bij elkaar.
def Mijnfilmsaanbiederscreen():
    global filmscreencheckint
    filmscreencheckint = 2
    BACKGROUND(mijnfilmsaanbiederframe, 'img/mijnfilms-a-background.png')
    mijnfilms_button = Button(master=mijnfilmsaanbiederframe, text='Films', command=lambda: toonFilmsAanbiederFrame(),
                            width=10, height=2, font=('Verdana', 14), activebackground="#ffcccc", background="#fff",
                            bd=0, fg="#b00000", border=0)
    mijnfilms_button.place(relx=0.11, rely=0.24, anchor=CENTER)
    user=username
    img_slide(mijnfilmsaanbiederframe, user, 1)
    uitlog_button(mijnfilmsaanbiederframe)

# Plaats frames, buttons en labels bij elkaar.

def back_button(frame, command):
    back_button = Button(master=frame, text="Back", command=command,font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    back_button.place(relx=0.82, rely=0.05, anchor=CENTER)


def Filmaanbiedenscreen(cover):
    global count
    count = 0
    BACKGROUND(filmaanbiedenframe, 'img/filmaanbieden-background.png')
    cur.execute('SELECT titel FROM Films WHERE cover=?', (cover,))
    titel = cur.fetchall()[0][0]
    showcover(filmaanbiedenframe, cover, 0.2, 0.58)
    showfilmtitel(filmaanbiedenframe, titel, 0.11, 0.28)
    showfilmdescription(filmaanbiedenframe, titel, 0.3, 0.35)
    showfilmdescriptionrate(filmaanbiedenframe,titel, 0.2, 0.35)
    back_button(filmaanbiedenframe,lambda:  toonFilmsAanbiederFrame())
    uitlog_button(filmaanbiedenframe)
    film_aanbieden_button = Button(master=filmaanbiedenframe, text="Film Aanbieden!",
                                 command=lambda: film_aanbieden_clicked(titel), font=('Verdana', 20),
                                 activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000", border=0)
    film_aanbieden_button.place(relx=0.82, rely=0.88, anchor=CENTER)
    showfilmdatum(filmaanbiedenframe, cover, 0.2, 0.88)

# Plaats frames, buttons en labels bij elkaar.
def Mijnfilmaanbiedenscreen(cover):
    BACKGROUND(mijnfilmaanbiedenframe, 'img/filmaanbieden-background.png')
    titel = gettitelfromcover(cover)
    showcover(mijnfilmaanbiedenframe, cover, 0.2, 0.58)
    showfilmtitel(mijnfilmaanbiedenframe, titel, 0.11, 0.28)
    uitlog_button(mijnfilmaanbiedenframe)
    back_button(mijnfilmaanbiedenframe, lambda: toonMijnFilmsAanbiederFrame())
    showgebruikersbijfilm(mijnfilmaanbiedenframe, titel, 0.32, 0.4)
    showfilmdatum(mijnfilmaanbiedenframe, cover, 0.2, 0.88)


def gettitelfromcover(cover):
    cur.execute('SELECT titel FROM Films WHERE cover=?', (cover,))
    titel = cur.fetchall()[0][0]
    return titel
def showgebruikersbijfilm(frame, titel, x, y):
    gebruikers = []
    cur.execute('SELECT User FROM Tickets WHERE Film = ?', (titel,))
    for gebruiker in cur.fetchall():
        gebruikers += [gebruiker[0]]
        plaats_button = 0
    for users in gebruikers:
        P = Button(frame, text=users, font=('Verdana', 12),command=lambda user = users: new_winF(user, titel), justify=LEFT).place(relx=x, rely=y+plaats_button, anchor=NW)
        plaats_button += 0.05


def new_winF(user, titel):
    cur.execute('SELECT code FROM Tickets WHERE Film = ? AND User = ?', (titel, user,))
    code = cur.fetchall()[0][0]
    newwin = Toplevel(root)
    display = Label(newwin, text="Controleer toegangscode voor de film {} als gast {}".format(titel, user))
    entry = Entry(newwin)
    button = Button(newwin, text='Controleer!', command=lambda: code_check_clicked(entry.get(), code))
    display.pack(pady=2)
    entry.pack(pady=2)
    button.pack(pady=2)

def code_check_clicked(codeinput, code):
    if  codeinput == code:
        popup('Toegangscode is juist!')
    else:
        popup('Verkeerde toegangscode!')

# Plaats frames, buttons en labels bij elkaar.
def Filmsgebruikerscreen():
    global filmscreencheckint
    filmscreencheckint = 3
    BACKGROUND(filmsgebruikerframe, 'img/films-a-background.png')
    user = username
    img_slide(filmsgebruikerframe, user, 0)
    mijnfilms_button = Button(master=filmsgebruikerframe, text='Mijn Films', command=lambda: toonMijnFilmsGebruikersFrame(),
                          width=10, height=2, font=('Verdana', 14), activebackground="#ffcccc", background="#fff", bd=0,
                          fg="#b00000", border=0)
    mijnfilms_button.place(relx=0.232, rely=0.24, anchor=CENTER)
    uitlog_button(filmsgebruikerframe)

def Mijnfilmsgebruikerscreen():
    global filmscreencheckint
    filmscreencheckint = 4
    BACKGROUND(mijnfilmsgebruikerframe, 'img/mijnfilms-a-background.png')
    user = username
    img_slide(mijnfilmsgebruikerframe, user, 3)
    films_button = Button(master=mijnfilmsgebruikerframe, text='Films', command=lambda: toonFilmsGebruikersFrame(),
                          width=10, height=2, font=('Verdana', 14), activebackground="#ffcccc", background="#fff", bd=0,
                          fg="#b00000", border=0)
    films_button.place(relx=0.11, rely=0.24, anchor=CENTER)
    uitlog_button(mijnfilmsgebruikerframe)

def Mijnfilmgebruikenscreen(cover):
    BACKGROUND(mijnfilmgebruikenframe, 'img/filmaanbieden-background.png')
    uitlog_button(mijnfilmgebruikenframe)
    back_button(mijnfilmgebruikenframe,lambda:  toonMijnFilmsGebruikersFrame())
    titel = gettitelfromcover(cover)
    showcover(mijnfilmgebruikenframe, cover, 0.2, 0.58)
    cur.execute('SELECT aanbieder FROM Films WHERE titel = ?', (titel,))
    aanbiederfilm = cur.fetchall()[0][0]
    ticketinfo = Label(master=mijnfilmgebruikenframe, text="Username:   {}\nAanbieder:   {}".format(username, aanbiederfilm), font=('Verdana', 14), background="#fff", justify=LEFT)
    showfilmdatum(mijnfilmgebruikenframe,cover,0.38, 0.45)
    ticketinfo.place(relx=0.3, rely=0.35, anchor=NW)
    showfilmtitel(mijnfilmgebruikenframe, titel, 0.11, 0.28)
    createqrcode(mijnfilmgebruikenframe, titel, 0.7, 0.57)
    Label(master=mijnfilmgebruikenframe, text=hashlib.sha256((username + titel).encode()).hexdigest(), background='#fff').place(relx=0.7, rely=0.85, anchor=CENTER)

def createqrcode(frame, titel, x, y):
    global code_bmp
    code = pyqrcode.create(hashlib.sha256((username + titel).encode()).hexdigest())
    code_bmp = BitmapImage(data=code.xbm(scale=6))
    code_bmp.config(background="white")
    label = Label(master=frame, image=code_bmp)
    label.place(relx=x, rely=y, anchor=CENTER)


def Filmgebruikenscreen(cover):
    BACKGROUND(filmgebruikenframe, 'img/filmaanbieden-background.png')
    titel = gettitelfromcover(cover)
    showcover(filmgebruikenframe, cover, 0.2, 0.58)
    showfilmtitel(filmgebruikenframe, titel, 0.11, 0.28)
    showfilmdescription(filmgebruikenframe, titel, 0.3, 0.35)
    showfilmdatum(filmgebruikenframe, cover, 0.2, 0.88)
    uitlog_button(filmgebruikenframe)
    back_button(filmgebruikenframe, lambda: toonFilmsGebruikersFrame())
    film_aanbieden_button = Button(master=filmgebruikenframe, text="Ticket kopen!",command=lambda: film_ticket_kopen_clicked(titel), font=('Verdana', 20),activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000", border=0)
    film_aanbieden_button.place(relx=0.82, rely=0.88, anchor=CENTER)


# Functie om de achtergrond te bepalen.
def BACKGROUND(frame, img):
    global filename
    background=Canvas(master=frame, height=750, width=1300)
    filename=PhotoImage(file=img)
    background_label=Label(master=frame, image=filename)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)
    background.pack()



# connectie met database
con = sqlite3.connect('film.db')
cur = con.cursor()

# bepaald de schermgroote van de GUI
display_x = "1300"
display_y = "750"

internet_check()

# GUI
root=Tk()


# Root Settings
root.title("HomeScoop")
root.geometry("{}x{}".format(display_x, display_y))
root.resizable(False, False)

# Frames
mijnfilmaanbiedenframe=Frame(master=root)
mijnfilmsaanbiederframe=Frame(master=root)
loginframe=Frame(master=root)
registerframe=Frame(master=root)
filmsaanbiederframe=Frame(master=root)
filmaanbiedenframe=Frame(master=root)
filmsgebruikerframe=Frame(master=root)
filmgebruikenframe=Frame(master=root)
mijnfilmsgebruikerframe=Frame(master=root)
mijnfilmgebruikenframe=Frame(master=root)

# Laat het eerste frame zien
toonLoginFrame()
root.mainloop()

# database sluiten
con.close()