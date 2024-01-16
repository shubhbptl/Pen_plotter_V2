!#/usr/bin/env bash
sudo docker build -t my_flask_v1 .

sudo docker run --device /dev/gpiomem -p 8080:8080 my_flask_v1

