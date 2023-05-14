import vpype
import vpype_gcode
import subprocess
from subprocess import run

# https://github.com/plottertools/vpype-gcode
# vpype -v to edit gwrite and other file 
# add new profile and upload: vpype -c /home/shubh/.local/lib/python3.10/site-packages/vpype_gcode/bundled_configs.toml
input_file = "/home/shubh/Pen_plotter_V2/my_flask/1683791677ScubaDiver2.svg"
output = "/home/shubh/Pen_plotter_V2/my_flask/out.svg"
subprocess.run(["vpype", "read", input_file, "linemerge", "-t 0.1mm", "linesort", "write", "--page-size","a2", "--center", output])
subprocess.run(["vpype", "read", input_file, "gwrite", "--profile", "my_own_plotter", 'butterfly.gcode'])