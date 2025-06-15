FROM python:3.11-slim

RUN apt-get update && \
    apt-get install --yes curl netcat-openbsd

RUN pip install --upgrade pip
RUN pip install --no-cache-dir nameko 

RUN groupadd -r nameko && useradd -r -g nameko -d /var/nameko nameko
RUN mkdir /var/nameko/ && chown -R nameko:nameko /var/nameko/
USER nameko
WORKDIR /var/nameko

#COPY requirements.txt .
#RUN pip install --no-cache-dir -r requirements.txt
COPY helloworld.py .
COPY conf.yml .
CMD ["nameko", "run", "--config", "conf.yml", "helloworld"]
