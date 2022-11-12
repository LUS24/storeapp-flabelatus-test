# CONTRIBUTING

## How to create a docker image

```commandline
docker build --no-cache -t store .

```

## How to run the Dockerfile locally

```commandline
docker run -dp 5005:5000 -w /app
 -v "/c/Users/scanlab/Desktop/pythonProject/updated_rest_api_course:/app" store

```

## The Dockerfile setup for development

```commandline
FROM python:3.10
EXPOSE 5000
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]

```