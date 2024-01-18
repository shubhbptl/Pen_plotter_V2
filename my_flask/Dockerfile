FROM python:3.9.2

WORKDIR /my_flask
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python3 -m pip install --user pipx
SHELL ["bash", "-lc"]
RUN python3 -m pipx ensurepath
RUN pipx install vpype\
    && pipx inject vpype hatched
COPY ./vpype.toml ./vpype.toml
RUN vpype --config ./vpype.toml
COPY ./templates ./templates
COPY ./static ./static
COPY main.py .
EXPOSE 8080

CMD python3 main.py