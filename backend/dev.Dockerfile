FROM python:3.8

WORKDIR /backend 

COPY requirements.txt /backend

RUN pip install -r requirements.txt

ENV FLASK_APP=manage.py
ENV FLASK_DEBUG=0
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

COPY . /backend

EXPOSE 5000

RUN chmod +x entrypoint.sh 

CMD [ "flask", "run", "--host", "0.0.0.0", "--port", "5000" ]
