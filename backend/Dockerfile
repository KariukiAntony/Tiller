FROM python:3.8

WORKDIR /backend 

COPY requirements.txt /backend

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt


COPY . /backend

EXPOSE 5000


CMD [ "gunicorn", "--bind", "", "0.0.0.0:5000", "--workers", "3", "run:app" ]