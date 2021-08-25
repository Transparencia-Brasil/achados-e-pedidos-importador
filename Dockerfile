FROM python:3.9.6
ENV PYTHONUNBUFFERED 1
ENV DJANGO_ENV dev
ENV DOCKER_CONTAINER 1
COPY ./requirements.txt /code/requirements.txt
RUN curl https://bootstrap.pypa.io/get-pip.py | python
RUN pip install -r /code/requirements.txt

COPY . /code/
WORKDIR /code/

RUN python manage.py collectstatic

EXPOSE 8000