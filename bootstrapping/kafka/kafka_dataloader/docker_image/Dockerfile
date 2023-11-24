FROM python:3.11

WORKDIR /home
COPY . ./

RUN pip install pipenv
RUN pip install pipenv && pipenv install --dev --system --deploy

CMD ["python", "./simple-producer.py"]
