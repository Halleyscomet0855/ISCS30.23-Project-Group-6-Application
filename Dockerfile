FROM python:3.11

WORKDIR /app

# RUN apt-get upgrade
# RUN apt install mysql-server -y
# RUN systemctl start mysql.service
# RUN apt install pip

RUN pip install Django==5.1.2
RUN pip install mysqlclient

COPY . . 

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0:8080"]

