FROM python:3.11-bullseye

WORKDIR /app

RUN adduser --system --no-create-home nonroot

RUN apt-get update &&  \
    apt-get -y upgrade &&  \
    apt-get -y install postgresql

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app

USER nonroot

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]