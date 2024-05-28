# Pen Plotter
### MHS/MVTHS Robotics and Enginering                
##### By: Shubh Patel, Roman Rice
---------------
## start server

1. start main server first, python3 /Main_Server/main.py
2. start processing server, python3 /Processing_Server/Server/processing_server.py
   
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
