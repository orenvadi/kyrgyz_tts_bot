FROM python:3.11

# set work directory
WORKDIR /usr/src/app/

# copy project
COPY . /usr/src/app/

# install dependencies
RUN pip install --user aiogram=2.23.1  python-dotenv requests

# run app
CMD ["python", "bot.py"]
