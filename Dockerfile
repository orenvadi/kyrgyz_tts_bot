FROM python:3.11

# set work directory
WORKDIR /usr/src/app/

# copy project
COPY . /usr/src/app/

# install dependencies
RUN pip install aiogram==2.23.1  python-dotenv requests

FROM ubuntu:latest as production

# run app
CMD ["python", "bot.py"]
