FROM python:3.7-alpine3.12

ENV PYTHONPATH /app

WORKDIR /app
ADD requirements-prod.txt .
ADD /auto_fork auto_fork

RUN pip install -r requirements-prod.txt

WORKDIR /app/auto_fork
CMD ["python", "app.py"]