FROM python:3.9.2

WORKDIR /my_flask
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY ./templates ./templates
COPY ./static ./static
COPY main.py .
EXPOSE 8080

CMD python3 main.py