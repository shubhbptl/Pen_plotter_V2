# Pen Plotter
### MHS/MVTHS Robotics and Enginering                
##### By: Shubh Patel, Roman Rice
---------------
# Requirement
```python
pip install -r requirements.txt
python3 -m pip install --user pipx
python3 -m pipx ensurepath
pipx install vpype\
&& pipx inject vpype hatched\
&& pipx inject vpype vpype-gcode
mv ./bundled_configs.toml /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
vpype -c /root/.local/share/pipx/venvs/vpype/lib/python3.9/site-packages/vpype_gcode/bundled_configs.toml
``` 
# Installation Guide

##  Step 1: change line of code 114,139 in Main.py
change to
```python
processing_url = "Your_Processing_Server_Ip/process"
```
your Ip address that your running your server on
Ex:
```python
processing_url = "10.1.57.108/process"
```
## Line 122 in processing_server.py
change to
```python
main_url = "Main_Server_URL/retrive"
```
your Ip address that your running your server on
Ex:
```python
main_url = "10.1.57.108/retrive"
```

## Step 2: Start the Main Server
First, start the main server by navigating to the Main_Server directory and running the main Python script.
```python3
python3 /Main_Server/main.py
```
## Step 3: Start the Processing Server
Next, start the processing server by navigating to the Processing_Server/Server directory and running the processing server script.
```python3
python3 /Processing_Server/Server/processing_server.py
```
## Utilization

1. Upload a file to the pen plotter server.
2. Preview the generated gcode.
3. Home the pen plotter.
4. load new paper 
5. Print!

# Important note 
## Emergency button 
If the prints fails to print or excceds print boundries.This will reset the Arduino and home itself.
## Reset-Alaram
Resets Grbl software and sets all the limits switch to idle. Only use this if the prints stop while running or Run out of boundries.
## Paper_Roller on & Off
This will allow you to turn on and off paper-Roller motor manually.
## Homing
This will home the pen to its origin.
## Print
This will print the current sketch from the /Main_Server/static/Image_Storage/Gcodes folder

# How everything works!
## img convert to gcode
The img user uploads get send to Processing Server which is build with flask, Img then get processed using library called Vpype which converts Img to gcode. The Processing Server send back the gcode of the img.

## Print the Gcode
For reading the gcode and printing it on paper. I'm using Grbl which is the backend of the pen-plotter. It only takes in Gcode. The Grbl firmware is uploaded into Metro-Mini. Raspberry Pi is connected to Metro-Mini through Uart Communication. Only job of Metro-Mini has to do is excute the gcode send by Raspberry pi.

## About This Project

This project was started by Shubh Patel during the 2022-2023 school year at the [Robotics and Engineering](https://mvthsengineering.com/) program of the [Medford Vocational Technical High School](https://mhs-mvths.mps02155.org/). It is currently still under active development.
