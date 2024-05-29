from flask import Flask, flash, redirect, render_template, request, Response
from werkzeug.utils import secure_filename
import requests
from subprocess import run
import subprocess
import os
import glob
import linedraw
app = Flask(__name__)

app.config["SECRET_KEY"] = "Gooseberry"
app.config["UPLOAD_FOLDER"] = os.path.join(
    app.root_path, "/home/mvths/shubh/Processing_Server/Processed_Images")  # saves all images uploaded
# saves all gcode converted from images and text folder
app.config["GCODE_FOLDER"] = os.path.join(
    app.root_path, "/home/mvths/shubh/Processing_Server/Processed_Gcode")

logo_filename = "/home/mvths/shubh/Processing_Server/Logo/logo.gcode"
current_Gcode = "/home/mvths/shubh/Processing_Server/Processed_Gcode/previous.gcode"

@app.route('/process', methods=['GET','POST'])
def process_image():
    prev_images = glob.glob(app.config["UPLOAD_FOLDER"] + '/*')
    for f in prev_images:
        os.remove(f)
        
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Convert the image to RGB mode if it's RGBA
        if file.mode == 'RGBA':
           file.convert('RGB')
         
        # Save the processed image
        filename = secure_filename(file.filename)
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(image_path)
        base_filename = os.path.splitext(filename)[0]
        ext_filename = os.path.splitext(filename)[1]
        print(ext_filename)
        
        
        if base_filename == "squiggly":
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),"rotate", "180","scaleto","200mm","200mm", "write",
                                   "--page-size", "450mmx300mm", "--center",  (os.path.join(app.config["UPLOAD_FOLDER"], "squiggly.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "squiggly.svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))]) 
        elif base_filename == "normal":
            subprocess.run(
                        [
                            "convert",
                            (os.path.join(
                                app.config["UPLOAD_FOLDER"], file.filename)),
                            "-gravity",
                            "East",
                            "-extent",
                            "100%x100%",
                            "-threshold",
                            "50%",
                            "-background",
                            "none",
                            "-alpha",
                            "remove",
                            "-negate",
                            (
                                os.path.join(
                                    app.config["UPLOAD_FOLDER"], "normal.svg"
                                )

                            ),
                        ]
                    )
                # convert svg to gcode
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "normal.svg")), "write",
                                   "--page-size", "450mmx300mm", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], "normal.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "normal.svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))]) 
        elif base_filename == "spiral":
            print("doing spiral")
            subprocess.run(["vpype", "hatched", "-c", (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),
                                   "write", (os.path.join(app.config["UPLOAD_FOLDER"], "spiral.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "spiral.svg")), "write",
                                   "--page-size", "450mmx300mm", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], "spiral.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "spiral.svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
        elif base_filename == "diagonal":
            print("doing diagonal")
            subprocess.run(["vpype", "hatched", (os.path.join(app.config["UPLOAD_FOLDER"], file.filename)),
                                   "write", (os.path.join(app.config["UPLOAD_FOLDER"], "diagonal.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "diagonal.svg")), "write",
                                   "--page-size", "450mmx300mm", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], "diagonal.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "diagonal.svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
        elif base_filename == "line_sketch":
            print("doing line_sketch")
            linedraw.draw_hatch = True
            linedraw.sketch((os.path.join(app.config["UPLOAD_FOLDER"], file.filename)))
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "line_sketch.svg")), "write",
                                   "--page-size", "450mmx300mm", "--center", (os.path.join(app.config["UPLOAD_FOLDER"], "line_sketch.svg"))])
            subprocess.run(["vpype", "read", (os.path.join(app.config["UPLOAD_FOLDER"], "line_sketch.svg")),
                                   "gwrite", "--profile", "my_own_plotter", (os.path.join(app.config["GCODE_FOLDER"], "previous.gcode"))])
        
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
        # sending back processed data
        gcode_path = os.path.join(app.config["GCODE_FOLDER"], "previous.gcode")       

        # Send the processed G-code content back to the main server
        main_url = "Main_Server_URL/retrive"
        files = {'gcode_file': open(gcode_path, 'rb')}
        response = requests.post(main_url, files=files)
        if response.status_code == 200:
            flash("Image has been uploaded and processed successfully.")
        else:
            flash("Failed to process the image.")
        return 'Image processed successfully and saved at: {}'.format(image_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
