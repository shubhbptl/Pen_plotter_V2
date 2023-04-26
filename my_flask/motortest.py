import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
motor_PWM = 12
motor_Direction = 15

GPIO.setup(motor_PWM,GPIO.OUT)
GPIO.setup(motor_Direction,GPIO.OUT)
motor = GPIO.PWM(motor_PWM,100)
motor.start(0)
while True:
    GPIO.output(motor_Direction, GPIO.LOW)
    GPIO.output(motor_PWM,100)
    time.sleep(0.1)