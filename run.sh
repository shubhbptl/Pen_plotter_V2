!#/usr/bin/env bash
sudo docker build -t my_flask_v1 .

sudo docker run --rm -p 8080:8080 --name penplotter my_flask_v1

