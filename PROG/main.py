import requests
import datetime
import xml.etree.ElementTree as ET

key = "z9rqxl4qlkw14ozm3z5721oscmu88zoz"
dag = datetime.datetime.now().strftime("%d-%m-%Y")
sorteer = "0"
api_url = 'http://api.filmtotaal.nl/filmsoptv.xml?apikey=' + key + '&dag=' + dag + '&sorteer=' + sorteer

response = requests.get(api_url)

print (response.text)
