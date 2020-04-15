from python:3.6.9
COPY . /usr/src/app
WORKDIR /usr/src/app
RUN pip install -r requirements.txt
CMD gunicorn -w 2 app:app --certfile=ssl/cert.pem --keyfile=ssl/key.pem -b 0.0.0.0:8443