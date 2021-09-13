FROM python:latest

WORKDIR /usr/local/bin

COPY . .

ENV TZ=Europe/Berlin

RUN pip install -r requirements.txt

CMD [ "python" , "-u" , "./qisbot.py" ]
