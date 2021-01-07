FROM python:3
ADD flask_api/ /flask_api
WORKDIR /flask_api
RUN apt-get update
RUN pip install -r requirements.txt
CMD python from app import db db.create_all() exit()
CMD flask run --host=0.0.0.0