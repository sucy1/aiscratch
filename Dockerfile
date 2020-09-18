FROM ubuntu:16.04

RUN apt-get update && apt-get install -y python3 python3-pip

ADD . /aiscratch/

WORKDIR /aiscratch/

RUN pip3 install -r requirements.txt -i https://pypi.douban.com/simple

RUN python3 manage.py makemigrations

RUN python3 manage.py migrate

CMD python3 manage.py runserver 0.0.0.0:8000
