FROM python:3.9.2

WORKDIR /my_flask

COPY requirements.txt .
COPY ./templates ./templates
COPY ./static ./static
COPY main.py .
EXPOSE 8080
RUN pip install -r requirements.txt

CMD python3 main.py