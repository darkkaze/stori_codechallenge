FROM python:3.9-bullseye
COPY requirements.txt requirements.txt
RUN apt update
RUN apt upgrade -y
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
RUN mkdir /app
WORKDIR /app
# CMD python3 /app/main.py