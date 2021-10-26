import requests
from pyquery import PyQuery
import schedule
import time
import os

user = os.environ['USER']
password = os.environ['PASSWORD']
degree = os.environ['DEGREE']
botToken = os.environ['BOT_TOKEN']
chatToken = os.environ['CHAT_TOKEN']


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + botToken + '/sendMessage?chat_id=' + chatToken + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()

def load_exams():
    url = "https://vorlesungen.tu-braunschweig.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal"

    data = {'asdf': user, 'fdsa': password, 'submit': 'Anmelden'}
    s = requests.Session() # save cookies
    print('Logging in to QIS...')
    x = s.post(url, data)

    # Prüfungsverwaltung
    pq = PyQuery(x.text)
    tag = pq('a.auflistung:contains("Prüfungsverwaltung")')
    link = tag.attr('href')
    print('Selecting "Prüfungsverwaltung"')
    x = s.get(link)

    pq = PyQuery(x.text)
    tag = pq('a.auflistung:contains("Info über angemeldete Prüfungen")')
    link = tag.attr('href')
    print('Selecting "Info über angemeldete Prüfung"')
    x = s.get(link)

    # Select degree
    pq = PyQuery(x.text)
    # this is needed if the user has multiple degrees
    tag = pq('a[title*="angemeldete Prüfungen anzeigen für ' + degree + '"]')
    link = tag.attr('href')
    print('Selecting the degree "' + degree + "'")
    x = s.get(link)

    # Print result
    pq = PyQuery(x.text)
    table = pq('table:contains("Prüfungsnr.")')
    rows = table.children('tr')
    message = 'The exams you are registered for:\n'
    print(message)
    for index, row in enumerate(rows):
        if (index < 2): continue
        line = PyQuery(row).children("td.mod_n").eq(1).text()
        message += '\n' + line
        print(line)

    telegram_bot_sendtext(message)

for i in ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]:
    schedule.every().monday.at(i).do(load_exams)
    schedule.every().tuesday.at(i).do(load_exams)
    schedule.every().wednesday.at(i).do(load_exams)
    schedule.every().thursday.at(i).do(load_exams)
    schedule.every().friday.at(i).do(load_exams)

while True:
    schedule.run_pending()
    time.sleep(60)
