import requests
from pyquery import PyQuery
import schedule
import time
import os
from py_pdf_parser.loaders import load_file

user = os.environ['USER']
password = os.environ['PASSWORD']
degree = os.environ['DEGREE']
botToken = os.environ['BOT_TOKEN']
chatToken = os.environ['CHAT_TOKEN']

url = "https://vorlesungen.tu-braunschweig.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm&breadCrumbSource=portal"
old_exams = []


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + botToken + \
        '/sendMessage?chat_id=' + chatToken + '&parse_mode=Markdown&text=' + bot_message

    response = requests.get(send_text)

    return response.json()


def login_to_qis():
    data = {'asdf': user, 'fdsa': password, 'submit': 'Anmelden'}
    session = requests.Session()  # save cookies
    print('Logging into QIS.')
    response = session.post(url, data)
    print('QIS Login successful.')
    return session, response


def load_registered_exams():
    session, response = login_to_qis()

    # Prüfungsverwaltung
    pq = PyQuery(response.text)
    tag = pq('a.auflistung:contains("Prüfungsverwaltung")')
    link = tag.attr('href')
    print('Selecting "Prüfungsverwaltung"')
    response = session.get(link)

    pq = PyQuery(response.text)
    tag = pq('a.auflistung:contains("Info über angemeldete Prüfungen")')
    link = tag.attr('href')
    print('Selecting "Info über angemeldete Prüfung"')
    response = session.get(link)

    # Select degree
    pq = PyQuery(response.text)
    # this is needed if the user has multiple degrees
    tag = pq('a[title*="' + degree + '"]')
    link = tag.attr('href')
    print('Selecting the degree "' + degree + '"')
    response = session.get(link)

    # return results
    pq = PyQuery(response.text)
    table = pq('table:contains("Prüfungsnr.")')
    rows = table.children('tr')
    registered_exams = []

    print('Extracting exams')

    for index, row in enumerate(rows):
        if (index < 2):
            continue
        registered_exams.append(PyQuery(row).children("td.mod_n").eq(1).text())
    return registered_exams


def load_grades():
    session, response = login_to_qis()

    # Prüfungsverwaltung
    pq = PyQuery(response.text)
    tag = pq('a.auflistung:contains("Prüfungsverwaltung")')
    link = tag.attr('href')
    print('Selecting "Prüfungsverwaltung"')
    response = session.get(link)

    # Notenspiegel
    pq = PyQuery(response.text)
    tag = pq('a.auflistung:contains("Notenspiegel")')
    link = tag.attr('href')
    print('Selecting "Info über angemeldete Prüfung"')
    response = session.get(link)

    # Select Degree
    pq = PyQuery(response.text)
    # this is needed if the user has multiple degrees
    tag = pq('a:contains("Abschluss: ' + degree + '")')
    link = tag.attr('href')
    print('Selecting the degree "' + degree + '"')
    response = session.get(link)

    pq = PyQuery(response.text)
    tag = pq('a[title*="Leistungen anzeigen"]')
    link = tag.attr('href')
    print('Selecting "Leistungen anzeigen"')
    # This call generates the pdf files
    response = session.get(link)

    # Download PDF
    pq = PyQuery(response.text)
    tag = pq('a[href*="hisreports"]')
    link = tag.attr('href')
    print('Start generating the PDF')
    response = session.get(link)

    print('Storing the PDF')

    try:
        os.remove("notenspiegel.pdf")
    except OSError:
        pass

    pdf = open("notenspiegel.pdf", 'wb')
    pdf.write(response.content)
    pdf.close()

    print('PDF stored')


def process_pdf(exams):
    document = load_file("notenspiegel.pdf")
    message = 'New grades found for following exams:\n'
    try:
        for exam in exams:
            # Disclaimer: We expect here that the graded element is the first one
            # with this specific name.
            # Sometimes it happens that a exam has two (or more) entries due to
            # stuff like passed homework or seminar or stuff.
            exam_element = document.elements.filter_by_text_contains(exam)[0]
            line = document.elements.to_the_right_of(exam_element)
            message += '\n' + exam + ': ' + line[len(line) - 1].text()
    except:
        message += "Can not extract the grade from the PDF."
    print(message)
    return message


def bot_run():
    global old_exams
    exams = load_registered_exams()

    if (len(exams) < len(old_exams)):
        print("New grades found!")
        load_grades()
        message = process_pdf(list(set(old_exams) - set(exams)))
        telegram_bot_sendtext(message)
        old_exams = exams
    else:
        print("No new grades found")


for i in ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]:
    schedule.every().monday.at(i).do(bot_run)
    schedule.every().tuesday.at(i).do(bot_run)
    schedule.every().wednesday.at(i).do(bot_run)
    schedule.every().thursday.at(i).do(bot_run)
    schedule.every().friday.at(i).do(bot_run)

# load registered exams on startup
old_exams = load_registered_exams()

while True:
    schedule.run_pending()
    time.sleep(60)
