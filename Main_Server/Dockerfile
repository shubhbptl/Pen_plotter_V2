FROM python:3.9.2

WORKDIR /my_flask
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python3 -m pip install --user pipx
SHELL ["bash", "-lc"]
RUN python3 -m pipx ensurepath
RUN pipx install vpype\
    && pipx inject vpype hatched\
    && pipx inject vpype vpype-gcode
COPY ./bundled_configs.toml /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
RUN vpype -c /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
COPY ./templates ./templates
COPY ./static ./static
COPY main.py .
EXPOSE 8080

CMD python3 main.py
