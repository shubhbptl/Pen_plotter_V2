from flask import Flask, flash, redirect, render_template, request, Response
from werkzeug.utils import secure_filename
from subprocess import run
import subprocess
import os
import glob
import serial


app = Flask(__name__, static_folder="static",)
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
current_Gcode = "static/Image_Storage/Gcodes/previous.gcode"
# location to small sketch needed for paper roller sensor that get added to current gcode file.
logo_filename = "static/Logo/logo.gcode"
firmware_file = 'UI_Buttons_Bash/firmware.txt'


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


port = '/dev/ttyUSB0'
baud = 115200


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
            if file and allowed_file(file.filename, ["jpg", "jpeg", "png", "bmp"]):
                print("Made it to allowed_file")
                # Delete Previous Image
                prev_images = glob.glob(app.config["UPLOAD_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)
                # converts png images to svg
                file.save(os.path.join(
                    app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
                resized_filename = file.filename
                if design == "normal":
                    print("doing normal")
                    subprocess.run(
                        [
                            "convert",
                            (os.path.join(
                                app.config["UPLOAD_FOLDER"], file.filename)),
                            "-gravity",
                            "East",
                            "-extent",
                            "105%x100%",
                            "-threshold",
                            "50%",
                            "-background",
                            "none",
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
                # convert svg to gcode
                    subprocess.run([cargo, (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg")),
                                   "--settings", setting, "-o", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
                elif design == "diagonal":
                    print("doing diagonal")
                    subprocess.run(["vpype", "hatched", (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),
                                   "write", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"))])
                    subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg")), "write",
                                   "--page-size", "10inx10in", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"))])
                    subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
                elif design == "spiral":
                    print("doing spiral")
                    subprocess.run(["vpype", "hatched", "-c", (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),
                                   "write", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"))])
                    subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg")), "write",
                                   "--page-size", "10inx10in", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg"))])
                    subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], resized_filename[:-4] + ".svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
                    # add small gcode to current gcode after it has been uploaded
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

                flash("Image has been Uploaded and Converted successfully.")
            else:
                flash("Invalid file format. Only JPG and PNG are allowed.")
            # converts PDF to gcode
        elif submit_button == "Upload PDF":
            file = request.files["file2"]
            if file and allowed_file(file.filename, ["pdf"]):
                # remove any previous pdf before uploading new pdf
                prev_images = glob.glob(app.config["TEXT_FOLDER"] + '/*')
                for f in prev_images:
                    os.remove(f)
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config["TEXT_FOLDER"], filename))
                # converts pdf to svg
                subprocess.run(["pdftocairo", (os.path.join(app.config["TEXT_FOLDER"], filename)), "-expand",
                               "-svg", (os.path.join(app.config["TEXT_FOLDER"], filename[:-4] + "resized.svg"))])
                # center the file
                subprocess.run(["vpype", "read", (os.path.join(app.config["TEXT_FOLDER"], filename[:-4] + "resized.svg")), "translate", "2cm", "0in", "linemerge", "--tolerance", "0.1mm", "linesort", "linesimplify", "write",
                                "--page-size", "14inx8.2in", (os.path.join(app.config["TEXT_FOLDER"], filename[:-4] + "resized.svg"))])
                # converts svg to gcode
                subprocess.run(["vpype", "read", (os.path.join(app.config["TEXT_FOLDER"], filename[:-4] + "resized.svg")),
                               "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
                flash("Text file has been Uploaded Successfully.")
            else:
                flash("Invalid file format. Only .pdf files are allowed.")
        return redirect("/")
    return render_template('index.html')


@app.route("/servo_up/")
def servo_up():
    try:
        ser = serial.Serial(port, baud, dsrdtr=True)
        flash(f"Connected to {port}")
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        # ser.write('\r\n\r\n'.encode())
        # time.sleep(2)
        # ser.flushInput()
        servoup = 'm3 s10' + '\n'
        ser.write(servoup.encode())
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
    try:
        ser = serial.Serial(port, baud, dsrdtr=True)
        flash(f"Connected to {port}")
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        ser.write('\r\n\r\n'.encode())
        time.sleep(0.1)
        ser.flushInput()
        servoDown = 'm3 s30' + '\n'
        ser.write(servoDown.encode())
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
    filename = os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")
    f = open(filename, 'r')
    try:
        ser = serial.Serial(port, baud, dsrdtr=True)
        flash(f"Connected to {port}")
        ser.write(('$X\n').encode())
        time.sleep(1)
        ser.write(('$H\n').encode())

        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")

    try:
        for line in f:
            l = line.strip()  # Strip all EOL characters for streaming
            print('Sending: ' + l,)
            ser.write((l + '\n').encode())  # Send g-code block to grbl
            grbl_out = ser.readline()  # Wait for grbl response with carriage return
            grbl_out_str = str(grbl_out)
            print(' : ' + grbl_out_str)
    except FileNotFoundError:
        flash(f"File {filename} not found")
        ser.close()
        return redirect('/')
    except:
        flash("Failed to upload G-code file")
        ser.close()
        return redirect('/')
    ser.write(('$H\n').encode())
    flash("Gcode Uploaded")
    ser.close()
    # motor roller
    return redirect("/")


@app.route("/homing/")
def homing():
    try:
        ser = serial.Serial(port, baud, dsrdtr=True)
        flash(f"Connected to {port}")
       # ser.write(('$X\n').encode())
       # flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        ser.write(('$H\n').encode())
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


@app.route("/reset_alarm/")  # press this button if the plotter stops
def reset_alarm():
    try:
        ser = serial.Serial(port, baud, dsrdtr=True)
        flash(f"Connected to {port}")
        ser.write(('$X\n').encode())
        flash("Alarm Unlocked")
    except serial.SerialException:
        flash(f"Failed to connect to {port}")
    try:
        ser.write(('$X\n').encode())
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
    app.run(host="0.0.0.0", port=8080, debug=True)
