from flask import Flask, flash, redirect, render_template, request
from werkzeug.utils import secure_filename
from subprocess import run
import os
from PIL import Image
import subprocess
from tqdm import tqdm
from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map
import time
from svg_to_gcode import TOLERANCES
import RPi.GPIO as GPIO
import time
app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "Gooseberry"
app.config["UPLOAD_FOLDER"] = "static/Image_Storage/Images/"
app.config["GCODE_FOLDER"] = "static/Image_Storage/Gcodes/"

SHELL_SCRIPT_DIRECTORY = "/home/pi/my_flask/UI_Buttons_Bash/"
#Hello

def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        submit_button = request.form.get("submit_button")
        size = request.form.get("size_selector")
        if submit_button == "Upload Image":
            file = request.files["file1"]
            if file and allowed_file(file.filename, ["jpg", "jpeg", "png"]):
                # Delete Previous Image
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
                flash("Image has been Uploaded Successfully.")
                img = Image.open(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

                if size == "small":
                    img_resize_lanczos = img.resize((100, 100), Image.LANCZOS)
                elif size == "medium":
                    img_resize_lanczos = img.resize((150, 150), Image.LANCZOS)
                elif size == "large":
                    img_resize_lanczos = img.resize((200, 200), Image.LANCZOS)

                resized_filename = "resized_" + secure_filename(file.filename)

                img_resize_lanczos.save(
                    os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
                )
                for i in tqdm(range(100), desc="Converting image to SVG: ", leave=True):
                    subprocess.run(
                        [
                            "convert",
                            (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),
                            "-threshold",
                            "50%",
                            "-background",
                            "white",
                            "-alpha",
                            "remove",
                            "-negate",
                            (
                                os.path.join(
                                    app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"
                                )
                                
                            ),
                        ]
                    )

                # Convert SVG to GCODE
                
                TOLERANCES['approximation'] = 0.01
                
                class CustomInterface(interfaces.Gcode):
                    def __init__(self):
                        super().__init__()
                        self.fan_speed = 1

                    def laser_off(self):
                        return "M03 S190;"

                    def set_laser_power(self, power):
                        if power < 0 or power > 1:
                            raise ValueError(f"{power} is out of bounds. Pen position must be given between 0 and 1. "
                                             f"The interface will scale it correctly.")

                        position = linear_map(0, 0, power)
                        return f"M03 S160;\n" + f"G1 Z{position:.2f} F2000;"

                gcode_compiler = Compiler(CustomInterface, movement_speed=1000, cutting_speed=200, pass_depth=0)

                curves = parse_file(os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"))

                gcode_compiler.append_curves(curves) 
                gcode_compiler.feed_rate = 2000  # Set the default feed rate to 2000 mm/min
                gcode_compiler.compile_to_file(os.path.join(app.config["GCODE_FOLDER"], "drawing.gcode"))

                flash("Image has been converted successfully.")

            else:
                flash("Invalid file format. Only JPG and PNG are allowed.")
        return redirect("/")
    return render_template('base.html')


@app.route("/servo_up/")
def servo_up():
    run([SHELL_SCRIPT_DIRECTORY + "Servo_Control/ServoUp.sh"], shell=True)
    return redirect("/")


@app.route("/servo_down/")
def servo_down():
    run([SHELL_SCRIPT_DIRECTORY + "Servo_Control/ServoDown.sh"], shell=True)
    return redirect("/")


@app.route("/connect/")
def Connect():
    run([SHELL_SCRIPT_DIRECTORY + "Connect.sh"], shell=True)
    return redirect("/")


@app.route("/Print/")
def Print():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(14, GPIO.OUT)
    GPIO.setup(15,GPIO.OUT)
    GPIO.output(14, GPIO.LOW)
    GPIO.output(15, GPIO.HIGH)
    time.sleep(20)
    GPIO.output(14, GPIO.LOW)
    GPIO.output(15, GPIO.LOW)
   # run([SHELL_SCRIPT_DIRECTORY + "Print.sh"], shell=True)
    return redirect("/")


@app.route("/homing/")
def homing():
    run([SHELL_SCRIPT_DIRECTORY + "Homing.sh"], shell=True)
    return redirect("/")


@app.route("/reset_alarm/")
def reset_alarm():
    run([SHELL_SCRIPT_DIRECTORY + "Reset_Alarm.sh"], shell=True)
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7000, debug=True)