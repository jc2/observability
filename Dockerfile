FROM python:3

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1 
# Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

WORKDIR /code
ADD https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-7.15.2-amd64.deb .
RUN dpkg -i filebeat-7.15.2-amd64.deb
COPY filebeat.yml /etc/filebeat/filebeat.yml

COPY requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY app.py /code/
COPY docker-entrypoint.sh /code/
ENTRYPOINT ["bash","docker-entrypoint.sh"]
