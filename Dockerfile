FROM python:3.11-bullseye

WORKDIR /app

RUN adduser --system --no-create-home nonroot

RUN apt-get update &&  \
    apt-get -y upgrade &&  \
    apt-get -y install postgresql

COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install

COPY . /app

USER nonroot

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]