FROM python:3
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir uWSGI
ENV DJANGO_SETTINGS_MODULE djirgha.settings
COPY . /app

CMD uwsgi --module=djirgha.wsgi:application --http-socket=:80
