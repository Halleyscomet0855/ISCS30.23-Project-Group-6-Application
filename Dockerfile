FROM python:3.11

WORKDIR /app

RUN pip install Django==5.1.2

COPY . . 

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0:8080"]

