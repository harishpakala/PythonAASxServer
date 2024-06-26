FROM python:3.9
WORKDIR PythonAASxServer
COPY . .
RUN pip install --upgrade pip --user
RUN pip install -r ./requirements.txt

CMD [ "python3.9","-u", "./src/main/pyaasxServer.py" ]

ENV TZ=Europe/Berlin
