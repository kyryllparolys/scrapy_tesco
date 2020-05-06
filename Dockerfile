FROM python:3
ENV PYTHONUNBUFFERED 1
RUN pip install "poetry==1.0.5"
RUN mkdir /code
WORKDIR /code
# COPY requirements.txt /code/
COPY poetry.lock pyproject.toml /code/
# RUN pip install -r requirements.txt
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi
COPY . /code/
RUN cd /code/src && scrapy crawl tesco -o tesco.json
