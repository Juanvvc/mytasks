FROM python:2.7-alpine
COPY . /app
WORKDIR /app
RUN apk add --update alpine-sdk libffi-dev libffi
RUN pip install -r requirements.txt
RUN apk del alpine-sdk libffi-dev
EXPOSE 8080
CMD ["gunicorn", "-w 3", "-b :8080", "manage:app"]
