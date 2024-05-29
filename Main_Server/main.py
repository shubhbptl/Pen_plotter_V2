from flask import Flask, flash, redirect, render_template, request, Response
from werkzeug.utils import secure_filename
from subprocess import run
import subprocess
import os
import requests
import glob
import serial
import time
import RPi.GPIO as GPIO
import re
import math
app = Flask(__name__, static_folder="static")
app.config["SECRET_KEY"] = "Gooseberry"
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "static/Image_Storage/Images")  # saves all images uploaded
# saves all gcode converted from images and text folder
app.config["GCODE_FOLDER"] = os.path.join(
    app.root_path, "static/Image_Storage/Gcodes")
app.config["TEXT_FOLDER"] = os.path.join(
    app.root_path, "static/Image_Storage/Text")      # save all Pdf uploaded
# converter for images to gcode
cargo = os.path.join(
    app.root_path, "/home/penplotter/Documents/svg2gcode/target/debug/svg2gcode")
# some required gcode parameter for this specific plotter
setting = os.path.join(
    app.root_path, "static/Setting/svg2gcode_settings.json")
# location to current gcode file
current_Gcode = "/home/penplotter/Pen_plotter_V2/static/Image_Storage/Gcodes/previous.gcode"
# location to small sketch needed for paper roller sensor that get added to current gcode file.
logo_filename = "static/Logo/logo.gcode"

firmware_file = 'UI_Buttons_Bash/firmware.txt'
hf2gcode = "/home/penplotter/Pen_plotter_V2/hf2gcode/src/hf2gcode"


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


port = '/dev/ttyAMA0'
baud = 115200
ser = serial.Serial(port, baud)

pin = 24
motor_Direction = 23
sensor1 = 22
motor_PWM = 18
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(pin, GPIO.OUT)
GPIO.setup(sensor1, GPIO.IN)
GPIO.setup(motor_Direction, GPIO.OUT)
GPIO.setup(motor_PWM, GPIO.OUT)
GPIO.output(pin, GPIO.LOW)
time.sleep(0.01)
GPIO.output(pin, GPIO.HIGH)


# vpype read /home/mvths/shubh/Processing_Server/Processed_Images/normal.svg squiggles -p 1 -a 5 write saodw.svg


@app.route("/retrive", methods=["GET", "POST"])
def retrive_gcode():
    if 'gcode_file' not in request.files:
        return 'No file part'
    file = request.files['gcode_file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Convert the image to RGB mode if it's RGBA
        if file.mode == 'RGBA':
            file.convert('RGB')
        # Save the processed image
        filename = secure_filename(file.filename)
        processed_image_path = os.path.join(
            app.config["GCODE_FOLDER"], filename)
        file.save(processed_image_path)
    return "got it"


@app.route("/squiggly")
def squiggly():
    return render_template('squiggly.html')


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        print("Made it to post")
        submit_button = request.form.get("submit_button")
        size = request.form.get("size_selector")
        design = request.form.get("design_selector")
        print(design)
        if submit_button == "upload_image":
            print("Made it to Upload Image")
            file = request.files["file1"]
            print(file)
            if file and allowed_file(file.filename, ["jpg", "jpeg", "png", "svg"]):
                print("Made it to allowed_file")
                # Delete Previous Image
                prev_images = glob.glob(app.config["UPLOAD_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)

                filename, ext = os.path.splitext(file.filename)
                new_filename = design + ext  # Construct the new filename

                # Save the file with the new filename
                image_path = os.path.join(
                    app.config['UPLOAD_FOLDER'], secure_filename(new_filename))
                file.save(image_path)

                processing_url = "Your_Processing_Server_Ip/process"
                files = {'file': open(image_path, 'rb')}
                response = requests.post(processing_url, files=files)
                if response.status_code == 200:
                    flash("Image has been uploaded and processed successfully.")
                else:
                    flash("Failed to process the image.")
                flash("Image has been Uploaded and Converted successfully.")
            else:
                flash("Invalid file format. Only JPG and PNG are allowed.")
            # converts PDF to gcode
        elif submit_button == "Upload SVG":
            file = request.files["fileSvg"]
            if (file and allowed_file(file.filename, ["svg"])):
                prev_images = glob.glob(app.config["TEXT_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)
                filename = secure_filename(file.filename)

                filename, ext = os.path.splitext(file.filename)
                new_filename = "squiggly" + ext
                image_path = os.path.join(
                    app.config['TEXT_FOLDER'], secure_filename(new_filename))
                file.save(image_path)

                processing_url = "Your_Processing_Server_Ip/process"
                files = {'file': open(image_path, 'rb')}
                response = requests.post(processing_url, files=files)
                if response.status_code == 200:
                    flash("Image has been uploaded and processed successfully.")
                else:
                    flash("Failed to process the image.")
                flash("Image has been Uploaded and Converted successfully.")
            else:
                flash("Invalid file format. Only JPG and PNG are allowed.")
        elif submit_button == "Upload PDF":
            file = request.files["file2"]
            if file and allowed_file(file.filename, ["txt"]):
                # remove any previous pdf before uploading new pdf
                prev_images = glob.glob(app.config["TEXT_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["TEXT_FOLDER"], filename))
                # converts pdf to svg
                f = open(os.path.join(
                    app.config["TEXT_FOLDER"], filename), "r")
                text = f.read()
                text = text.replace('\t', '    ')
                f.close()

                out = open(os.path.join(
                    app.config["TEXT_FOLDER"], filename), "w")
                out.seek(0)
                out.write(text)
                out.flush()
                out.close()
                subprocess.run(['hf2gcode', '-i', (os.path.join(app.config["TEXT_FOLDER"], filename)), '-s', '0.3',
                               '-n', '9', '-m', '-p', '7', '-f', '2500', '--z-down=72', '--z-up=45', '-l', '-x', '-600', '-y', '-100', '-o', (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
                f = open(
                    (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")), "r")
                text = f.read()
                text = re.sub("G0 Z.*", "M3 s45"+'\n'+'G4 p0.3.1\n', text)
                text = re.sub("M3 S10000", "", text)
                text = re.sub("M5", "M3 s72", text)
                text = re.sub("G1 Z.*", "M3 s72"+'\n'+'G4 p0.3\n', text)
                f.close()
                out = open(
                    (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")), "w")
                out.seek(0)
                out.write(text)
                out.flush()
                out.close()
                process_gcode((os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")),(os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")),180)
                with open(logo_filename, 'r') as f:
                    data = f.read()
                    f.close()

                with open(current_Gcode, 'r') as f:
                    old_data = f.read()
                    f.close()

                with open(current_Gcode, 'w') as f:
                    f.write(data)
                    f.write(old_data)
                    f.close()
            else:
                flash("Invalid file format. Only .pdf files are allowed.")
        elif submit_button == "Send Gcode":
            file = request.form["text"]
            try:
                if (file == ""):
                    return redirect("/")
                ser.write((file + "\n").encode())
                flash(file)
            except serial.SerialException:
                flash(f"Failed to connect to {port}")

                return redirect("/")
            while ser.in_waiting != 0:
                response = ser.readline(1000)
                flash(response)
                pass


        return redirect("/")
    return render_template('index.html')

def apply_equation(x, y, angle):
    new_x = x * math.cos(angle) - y * math.sin(angle)
    new_y = x * math.sin(angle) + y * math.cos(angle)
    return new_x, new_y

def process_gcode(input_file, output_file, angle):
    with open(input_file, "r") as f:
        gcode = f.read()
        # Apply equation to X and Y coordinates
        new_gcode = re.sub(
        r"(X|Y)(-?\d+\.?\d*)",
        lambda match: f"{match.group(1)}{apply_equation(float(match.group(2)), 0, angle)[0]:.4f}"
        if match.group(1) == "X"
        else f"{match.group(1)}{apply_equation(0, float(match.group(2)), angle)[1]:.4f}",
        gcode)  
        # Write modified G-code to output file
        with open(output_file, "w") as f:
            f.write(new_gcode) 

@app.route("/paper_roller_on/")
def paper_roller_on():
    GPIO.output(motor_Direction, GPIO.HIGH)
    GPIO.output(motor_PWM, GPIO.HIGH)
   # motor.ChangeDutyCycle(85)
    return render_template('index.html')


@app.route("/paper_roller_off/")
def paper_roller_off():
    GPIO.output(motor_Direction, GPIO.HIGH)
    GPIO.output(motor_PWM, GPIO.LOW)

    return render_template('index.html')


@app.route("/servo_up/")
def servo_up():
    try:
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        ser.write('\r\n\r\n'.encode())
        time.sleep(0.01)
        ser.flush()
        servoup = 'm3 s45' + '\n'
        ser.write(servoup.encode())
        flash("Servo down command sent")
    except Exception as e:
        flash(f"Failed to send servo down command: {e}")

        return redirect('/')
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Servo up response: {response}")
    return redirect('/')


@app.route("/servo_down/")
def servo_down():
    try:
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        ser.write('\r\n\r\n'.encode())
        time.sleep(0.01)
        ser.flush()
        servoDown = 'm3 s72' + '\n'
        ser.write(servoDown.encode())
        flash("Servo up command sent")
    except Exception as e:
        flash(f"Failed to send servo up command: {e}")

        return redirect('/')
    while ser.in_waiting == 0:
        pass
    
    response = ser.readlines()
    flash(f"Servo up response: {response}")
    return redirect("/")


@app.route("/Print/")
def Print():
    filename = os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")
    f = open(filename, 'r')
    try:
        ser.write(('$X\n').encode())
        time.sleep(0.1)
        ser.write(('$H\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")

    while True:

        if GPIO.input(sensor1) == 1:
            GPIO.output(motor_Direction, GPIO.HIGH)
            GPIO.output(motor_PWM, GPIO.HIGH)
        else:
            time.sleep(1)
            GPIO.output(motor_Direction, GPIO.LOW)
            GPIO.output(motor_PWM, GPIO.LOW)
            time.sleep(0.5)
            break
    try:
        ser.write('\r\n\r\n'.encode())
        time.sleep(0.01)
        ser.flushInput()
        ser.write(('$H\n').encode())
        for line in f:
            l = line.strip()  # Strip all EOL characters for streaming
            print('Sending: ' + l,)
            ser.write((l + '\n').encode())  # Send g-code block to grbl
            grbl_out = ser.readline()  # Wait for grbl response with carriage return
            grbl_out_str = str(grbl_out)
            print(' : ' + grbl_out_str)
    except FileNotFoundError:
        flash(f"File {filename} not found")

        return redirect('/')
    except:
        flash("Failed to upload G-code file")

        return redirect('/')
    ser.write(('$H\n').encode())
    flash("Gcode Uploaded")
    # motor roller

    return redirect("/")


@app.route("/homing/")
def homing():
    try:
        ser.write(('$H\n').encode())
        ser.write(('G10 P0 L20 X0 Y0 Z0\n').encode())
        flash("Homing command sent")
    except Exception as e:
        flash(f"Failed to send homing command: {e}")
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Homing response: {response}")
    return redirect("/")

@app.route("/emergency_stop/")
def emergency_stop():
    try:
        ser.close()
        ser.open()
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(1.5)
        ser.write(('$X\n').encode())
        servoup = 'm3 s45' + '\n'
        ser.write(servoup.encode())
        ser.write(('$H\n').encode())
        flash("Alarm reset command sent")
    except Exception as e:
        flash(f"Failed to send alarm reset command: {e}")
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Alarm reset response: {response}")
    return redirect("/")


@app.route("/reset_alarm/")  # press this button if the plotter stops
def reset_alarm():
    try:
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        GPIO.output(pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.output(pin, GPIO.HIGH)
        ser.write(('$X\n').encode())
        flash("Alarm reset command sent")
    except Exception as e:
        flash(f"Failed to send alarm reset command: {e}")
    while ser.in_waiting == 0:
        pass
    response = ser.readline()
    flash(f"Alarm reset response: {response}")
    return redirect("/")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
