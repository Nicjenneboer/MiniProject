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

def toonMijnFilmsAanbiederFrame():
    filmsaanbiederframe.pack_forget()
    mijnfilmsaanbiederframe.pack()
    Mijnfilmsaanbiederscreen()

def toonLoginFrame():
    filmaanbiedenframe.pack_forget()
    gebruikerhoofdframe.pack_forget()
    registerframe.pack_forget()
    filmsaanbiederframe.pack_forget()
    mijnfilmsaanbiederframe.pack_forget()
    loginframe.pack()
    Loginscreen()

def toonGebruikerHoofdFrame():
    loginframe.pack_forget()
    registerframe.pack_forget()
    gebruikerhoofdframe.pack()

def toonRegisterFrame():
    loginframe.pack_forget()
    gebruikerhoofdframe.pack_forget()
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
                    cur.fetchall()
                    toonFilmsAanbiederFrame()
                wrong = False
            else:
                wrong = True
        else:
            wrong = True
    if wrong == True:
        popup('Verkeerde inlog gegevens!')



def registreer_clicked(auth, usern, userp, userpc):
    gebruikersnaambestaatniet = False
    naam = usern
    autho = auth
    ww = hashlib.sha256(userp.encode()).hexdigest()
    if userp == userpc:
        cur.execute('SELECT * FROM Users')
        for i in cur:
            if naam == i[0]:
                gebruikersnaambestaatniet = False
                break
            else:
                gebruikersnaambestaatniet = True
        if gebruikersnaambestaatniet == True:
            record = (naam, ww, autho)
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
#GUI FRAMES

def popup(bericht):
    showinfo(title='popup', message=bericht)

def Loginscreen():
    global wrong_input_login
    BACKGROUND(loginframe, 'img/loginbackground.png')
    username_entry = Entry(master=loginframe, width=25, font=('Verdana', 15))
    userpass_entry = Entry(master=loginframe, width=25, font=('Verdana', 15), show="*")
    username_label = Label(master=loginframe, text="Gebruikersnaam:", font=('Verdana', 15))
    userpass_label = Label(master=loginframe, text="Wachtwoord:", font=('Verdana', 15))
    login_button = Button(master=loginframe, text="Login!",command=lambda: login_clicked(username_entry.get(), userpass_entry.get()),font=('Verdana', 20), activebackground="#b00000", background="#d00000", bd=0, fg="#fff")
    registreerframe_button = Button(master=loginframe, text="Maak een account aan.", command=lambda: toonRegisterFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    wrong_input_login = Label(master=loginframe, text="", font=('Verdana', 15))
    # Place
    username_label.place(relx=0.3, rely=0.58, anchor=CENTER)
    userpass_label.place(relx=0.315, rely=0.63, anchor=CENTER)
    username_entry.place(relx=0.52, rely=0.58, anchor=CENTER)
    userpass_entry.place(relx=0.52, rely=0.63, anchor=CENTER)
    login_button.place(relx=0.70, rely=0.605, anchor=CENTER)
    registreerframe_button.place(relx=0.85, rely=0.05, anchor=CENTER)
    wrong_input_login.place(relx=0.5, rely=0.53, anchor=CENTER)




def Registerscreen():
    BACKGROUND(registerframe, 'img/registreerbackground.png')
    v = IntVar()
    aanbieder = Radiobutton(registerframe, text="Aanbieder", variable=v, value=1,font=('Verdana', 12))
    gebruiker = Radiobutton(registerframe, text="Gebruiker", variable=v, value=0,font=('Verdana', 12))
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

def film_img_slide(next):
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
    cur.execute('SELECT cover FROM Films WHERE aanbieder = "0"')
    filmimglist = []
    filmtitellist = []
    for cover in cur:
        filmimglist += [cover[0]]
    if count < 0:
        count = 0
    elif count > len(filmimglist) - 4:
        count = len(filmimglist) - 4
    for i in range(4):
        my_page = urlopen(filmimglist[i+count])
        my_picture = io.BytesIO(my_page.read())
        pil_img = Image.open(my_picture)
        if i == 0:
            tk_img1 = ImageTk.PhotoImage(pil_img)
            film1 = Button(filmsaanbiederframe, image=tk_img1, command=lambda: toonFilmAanbiedenFrame(filmimglist[i+count-3]))
        elif i == 1:
            tk_img2 = ImageTk.PhotoImage(pil_img)
            film2 = Button(filmsaanbiederframe, image=tk_img2, command=lambda: toonFilmAanbiedenFrame(filmimglist[i+count-2]))
        elif i == 2:
            tk_img3 = ImageTk.PhotoImage(pil_img)
            film3 = Button(filmsaanbiederframe, image=tk_img3, command=lambda: toonFilmAanbiedenFrame(filmimglist[i+count-1]))
        elif i == 3:
            tk_img4 = ImageTk.PhotoImage(pil_img)
            film4 = Button(filmsaanbiederframe, image=tk_img4, command=lambda: toonFilmAanbiedenFrame(filmimglist[i+count]))
    film1.place(relx=0.2, rely=0.6, anchor=CENTER)
    film2.place(relx=0.4, rely=0.6, anchor=CENTER)
    film3.place(relx=0.6, rely=0.6, anchor=CENTER)
    film4.place(relx=0.8, rely=0.6, anchor=CENTER)

def showcover(frame, url, x, y):
    global tk_img
    my_page = urlopen(url)
    my_picture = io.BytesIO(my_page.read())
    pil_img = Image.open(my_picture)
    tk_img = ImageTk.PhotoImage(pil_img)
    label = Label(frame, image=tk_img)
    label.place(relx=x, rely=y, anchor=CENTER)

def showfilmdescription(frame, titel, x, y):
    cur.execute('SELECT synopsis FROM Films WHERE titel=?', (titel,))
    desc = cur.fetchall()[0][0]
    p = '\n'.join(desc[i:i + 120] for i in range(0, len(desc), 120))
    label = Label(master=frame, background='#fff' ,text=p,justify=LEFT)
    label.place(relx=x, rely=y, anchor=NW)

def Filmsaanbiederscreen():
    global count
    count = 0
    BACKGROUND(filmsaanbiederframe, 'img/films-a-background.png')
    films_button = Button(master=filmsaanbiederframe,text='Mijn Films',command=lambda: toonMijnFilmsAanbiederFrame(), width=10, height=2,font=('Verdana', 14), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    films_button.place(relx=0.232, rely=0.24, anchor=CENTER)
    film_img_slide(0)
    next = Button(master=filmsaanbiederframe, text=">", command=lambda: film_img_slide(1) )
    next.place(relx=0.92, rely=0.6, anchor=CENTER)
    back = Button(master=filmsaanbiederframe, text="<", command=lambda: film_img_slide(2))
    back.place(relx=0.08, rely=0.6, anchor=CENTER)
    uitlog_button = Button(master=filmsaanbiederframe, text="Uitloggen",command=lambda: toonLoginFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    uitlog_button.place(relx=0.92, rely=0.05, anchor=CENTER)

def Filmaanbiedenscreen(cover):
    BACKGROUND(filmaanbiedenframe, 'img/filmaanbieden-background.png')
    cur.execute('SELECT titel FROM Films WHERE cover=?', (cover,))
    titel = cur.fetchall()[0][0]
    showcover(filmaanbiedenframe, cover, 0.2, 0.58)
    showfilmdescription(filmaanbiedenframe, titel, 0.3, 0.35)
    back_button = Button(master=filmaanbiedenframe, text="Back", command=lambda: toonFilmsAanbiederFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    back_button.place(relx=0.82, rely=0.05, anchor=CENTER)
    uitlog_button = Button(master=filmaanbiedenframe, text="Uitloggen",command=lambda: toonLoginFrame(),font=('Verdana', 20), activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000",border=0)
    uitlog_button.place(relx=0.92, rely=0.05, anchor=CENTER)
def Mijnfilmsaanbiederscreen():
    mijnfilmsaanbiederframe.pack()
    BACKGROUND(mijnfilmsaanbiederframe, 'img/mijnfilms-a-background.png')
    mijnfilms_button = Button(master=mijnfilmsaanbiederframe, text='Films',command=lambda: toonFilmsAanbiederFrame(), width=10, height=2, font=('Verdana', 14),activebackground="#ffcccc", background="#fff", bd=0, fg="#b00000", border=0)
    mijnfilms_button.place(relx=0.11, rely=0.24, anchor=CENTER)



def gebruiker_login():
    toonGebruikerHoofdFrame()
    login_succes_welkom_label = Label(master=gebruikerhoofdframe, text="Welkom gebruiker!")
    login_succes_welkom_label.pack(pady=10)
    b = Button(master=gebruikerhoofdframe, command=lambda: toonLoginFrame(), width=12, height=12)
    b.pack(pady=10)



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
mijnfilmsaanbiederframe = Frame(master=root)
loginframe = Frame(master=root)
gebruikerhoofdframe = Frame(master=root)
registerframe = Frame(master=root)
filmsaanbiederframe = Frame(master=root)
filmaanbiedenframe = Frame(master=root)




toonFilmsAanbiederFrame()
root.mainloop()

con.close()



