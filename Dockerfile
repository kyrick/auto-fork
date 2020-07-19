FROM python:3.7-alpine3.12

WORKDIR /app
ADD requirements.txt .
ADD /auto_fork .

RUN pip install -r requirements.txt

CMD ["python","app.py"]