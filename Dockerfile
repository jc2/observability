FROM python:3.9.6-alpine

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1 
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

WORKDIR /code
# ADD https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.15.2-amd64.deb .
# RUN dpkg -i filebeat-7.15.2-amd64.deb
# COPY filebeat.yml /etc/filebeat/filebeat.yml

# create directory for the app logs
RUN mkdir -p /logs/app

COPY requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py /code/
COPY custom_logger.py /code/

COPY docker-entrypoint.sh /code/
RUN sed -i 's/\r$//g' /code/docker-entrypoint.sh
RUN chmod +x /code/docker-entrypoint.sh

ENTRYPOINT ["/code/docker-entrypoint.sh"]
