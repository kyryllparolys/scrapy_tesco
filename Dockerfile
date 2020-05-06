FROM python:3.6.6
ENV YOUR_ENV=${YOUR_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.0.5

RUN pip install "poetry==$POETRY_VERSION"
RUN mkdir /code
WORKDIR /code
# COPY requirements.txt /code/
COPY poetry.lock pyproject.toml /code/
# RUN pip install -r requirements.txt
RUN poetry config virtualenvs.create false \
  && poetry install
COPY . /code/
RUN cd /code/src && scrapy crawl tesco -o tesco.json
