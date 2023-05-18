from flask import Flask, flash, redirect, render_template, request, Response
from werkzeug.utils import secure_filename
from subprocess import run
import subprocess
import os
import glob
from PIL import Image
from tqdm import tqdm
import serial
import time
from svg_to_gcode import TOLERANCES
from asyncio import sleep
app = Flask(__name__, static_folder="static",)
app.config["SECRET_KEY"] = "Gooseberry"
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "/home/shubh/Pen_plotter_V2/my_flask/static/Image_Storage/Images")
app.config["GCODE_FOLDER"] = os.path.join(app.root_path, "/home/shubh/Pen_plotter_V2/my_flask/static/Image_Storage/Gcodes")
app.config["TEXT_FOLDER"] = os.path.join(app.root_path, "/home/shubh/Pen_plotter_V2/my_flask/static/Image_Storage/Text")



def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        submit_button = request.form.get("submit_button")
        size = request.form.get("size_selector")
        if submit_button == "Upload Image":
            file = request.files["file1"]
            if file and allowed_file(file.filename, ["jpg", "jpeg", "png", "bmp", "webp", "pdf"]):
                # Delete Previous Image
                prev_images = glob.glob(app.config["UPLOAD_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
                flash("Image has been Uploaded Successfully.")
                img = Image.open(os.path.join(app.config["UPLOAD_FOLDER"], file.filename))

                if size == "small":
                    img_resize_lanczos = img.resize((100, 200), Image.LANCZOS)
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
                            os.path.join(app.config["UPLOAD_FOLDER"], file.filename),
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
                reformed_filename = "reformed" + resized_filename[:-4]+ ".svg"
                # Convert SVG to GCODE

                subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4]+ ".svg")), "gwrite", "--profile", "gcode", (os.path.join(app.config["GCODE_FOLDER"], "Pervious.gcode"))])
                flash("Image has been converted successfully.")
            else:
                flash("Invalid file format. Only JPG and PNG are allowed.")
        elif submit_button == "Upload PDF":
            file = request.files["file2"]
            if file and allowed_file(file.filename, ["pdf"]):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["TEXT_FOLDER"], filename))
                subprocess.run(["pdf2svg",(os.path.join(app.config["TEXT_FOLDER"], filename)),(os.path.join(app.config["TEXT_FOLDER"], filename[:-4]+ "resized.svg"))])
                subprocess.run(["vpype", "read", (os.path.join(app.config["TEXT_FOLDER"], filename[:-4]+ "resized.svg")), "gwrite", "--profile", "gcode", (os.path.join(app.config["GCODE_FOLDER"], "pervious.gcode"))])
                flash("Text file has been Uploaded Successfully.")
            else:
                flash("Invalid file format. Only .pdf files are allowed.")
        return redirect("/")
    return render_template('base.html')


@app.route("/servo_up/")
def servo_up():
    port = '/dev/ttyUSB0'
    baud = 115200
    try:
        ser = serial.Serial(port, baud)
        flash(f"Connected to {port}")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
        return redirect('/')
        
    time.sleep(2)
    try:
        ser.write(b'M03 S190;\n'.encode())
        flash("Servo down command sent")
    except Exception as e:
        flash(f"Failed to send servo down command: {e}")
        ser.close()
        return redirect('/')
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Servo up response: {response}")
    ser.close() 
    return redirect('/')

@app.route("/servo_down/")
def servo_down():
    port = '/dev/ttyUSB0'
    baud = 115200
    try:
        ser = serial.Serial(port, baud)
        flash(f"Connected to {port}")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
        return redirect('/')
    time.sleep(2)
    try:
        ser.write(b'M03 S150;\n'.encode())
        flash("Servo up command sent")
    except Exception as e:
        flash(f"Failed to send servo up command: {e}")
        ser.close()
        return redirect('/')
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Servo up response: {response}")
    ser.close()
    return redirect("/")

@app.route("/Print/")
def Print():
    port = '/dev/ttyUSB0'
    baud = 115200
    #firmware_file = '/home/penplotter/Pen_plotter_V2/my_flask/UI_Buttons_Bash/firmware_2022-15-01.settings'
    
    
    try:
        ser = serial.Serial(port, baud)
        flash(f"Connected to {port}")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
        return redirect('/')
    time.sleep(2)
    filename = os.path.join(app.config["GCODE_FOLDER"], "drawing.gcode")
    try:
        with open(filename, 'r') as f:
            for line in f:
                line = line.split(';')[0]
                ser.write((line + '\n').encode())
                while ser.in_waiting == 0:
                    pass
            flash("Gcode Uploaded")
    except FileNotFoundError:
        flash(f"File {filename} not found")
        ser.close()
        return redirect('/')
    except:
        flash("Failed to upload G-code file")
        ser.close()
        return redirect('/')
    ser.close()
    return redirect("/")


@app.route("/homing/")
def homing():
    port = '/dev/ttyUSB0'
    baud = 115200
    try:
        ser = serial.Serial(port, baud)
        flash(f"Connected to {port}")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
        return redirect('/')
    time.sleep(2)
    try:
        ser.write(b'$H\n'.encode())
        flash("Homing command sent")
    except Exception as e:
        flash(f"Failed to send homing command: {e}")
        ser.close()
        exit()
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Homing response: {response}")
    ser.close()
    return redirect("/")


@app.route("/reset_alarm/")
def reset_alarm():
    port = '/dev/ttyUSB0'
    baud = 115200
    try:
        ser = serial.Serial(port, baud)
        flash(f"Connected to {port}")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
        return redirect('/')
    time.sleep(2)
    try:
        ser.write(b'$X\n'.encode())
        flash("Alarm reset command sent")
    except Exception as e:
        flash(f"Failed to send alarm reset command: {e}")
        ser.close()
        exit()
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Alarm reset response: {response}")
    ser.close()
    return redirect("/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
