FROM python:3.7-slim

RUN mkdir /krishabot

COPY requirements.txt /krishabot

RUN pip3 install -r /krishabot/requirements.txt --no-cache-dir

COPY . /krishabot

WORKDIR /krishabot

CMD [ "python", "./krisha_parser.py" ]
