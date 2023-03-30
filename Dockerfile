FROM python:3.7
WORKDIR PythonAASxServer
COPY . .

RUN pip3 install -r ./requirements.txt

CMD [ "python3","-u", "./src/main/pyaasxServer.py" ]

ENV TZ=Europe/Berlin