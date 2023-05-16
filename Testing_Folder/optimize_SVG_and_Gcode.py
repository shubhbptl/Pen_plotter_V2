import subprocess
from subprocess import run

# https://github.com/plottertools/vpype-gcode
# vpype -v to edit gwrite and other file 
# add new profile and upload: vpype -c /home/shubh/.local/lib/python3.10/site-packages/vpype_gcode/bundled_configs.toml
input_file = "/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Images/bmp3-infantry-fighting-vehicle-icon-260nw-2142006461.webp"
output = "/home/penplotter/Pen_plotter_V2/out.svg"
text = "/home/penplotter/Pen_plotter_V2/text.txt"
#vpype = vpype text --help
#subprocess.run(["vpype", "read", input_file, "linemerge", "-t 0.1mm", "linesort", "write", "--page-size","a2", "--center", output])
subprocess.run(["vpype", "text", text, "gwrite", "--profile", "my_own_plotter", 'butterfly.gcode'])

#-------------------------------------------------------------------------------------------------------------------
#Control position and alignment
#vpype text --position 0 0 "Hello world" text --position 0 1cm --align right "dlrow olleH" text --position 0 2cm --align center "Hello olleH" show
# -------------------------------------------------------------------------------------------------------------------
#change text font and size
#vpype text "Default font and size" text -p 0 1cm --font gothiceng -s 12px "Custom font and size" show
