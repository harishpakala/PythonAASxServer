FROM python:3.7
WORKDIR testsample
COPY . .

RUN pip3 install APScheduler python-snap7 opcua pybars3 paho-mqtt flask werkzeug  Flask Flask-RESTful pymongo python-dotenv requests jsonschema web3

CMD [ "python3","-u", "./src/main/testsample.py" ]

ENV TZ=Europe/Berlin