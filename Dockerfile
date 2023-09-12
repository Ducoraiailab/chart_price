FROM python:3.8.5-slim-buster

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN python -m pip install --upgrade pip
RUN pip install --upgrade -r /code/requirements.txt
COPY . /code

#CMD ["python3","app.py"]
