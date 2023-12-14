FROM python:3.11

WORKDIR /home
COPY ./data data/
COPY ./program program/
COPY Pipfile Pipfile.lock .

RUN pip install pipenv
RUN pip install pipenv && pipenv install --dev --system --deploy

# Change dir to the program folder so that the data file path works
WORKDIR program 
CMD ["python", "simple-producer.py"]
