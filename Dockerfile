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
RUN apt-get update && apt-get install wget build-essential cmake libfreetype6-dev pkg-config libfontconfig-dev libjpeg-dev libopenjp2-7-dev -y
COPY poppler-data-0.4.9.tar.gz .
RUN tar -xf poppler-data-0.4.9.tar.gz \
    && cd poppler-data-0.4.9 \
    && make install \
    && cd .. \
    && wget https://poppler.freedesktop.org/poppler-20.08.0.tar.xz \
    && tar -xf poppler-20.08.0.tar.xz \
    && cd poppler-20.08.0 \
    && mkdir build \
    && cd build \
    && cmake .. \
    && make \
    && make install \
    && ldconfig
RUN pdftocairo -v
COPY ./bundled_configs.toml /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
RUN vpype -c /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
COPY ./templates ./templates
COPY ./static ./static
COPY main.py .
EXPOSE 8080

CMD python3 main.py