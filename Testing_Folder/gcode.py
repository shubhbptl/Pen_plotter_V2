from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces
from svg_to_gcode.formulas import linear_map

class CustomInterface(interfaces.Gcode):
    def __init__(self):
        super().__init__()
        self.fan_speed = 1

    # Override the laser_off method such that it also powers off the fan.
    def laser_off(self):
        return "M3 S150;\n G4 P0.2;\n"  # Turn off the fan + turn off the laser

    # Override the set_laser_power method
    def set_laser_power(self, power):
        if power < 0 or power > 1:
            raise ValueError(f"{power} is out of bounds. Laser power must be given between 0 and 1. "
                             f"The interface will scale it correctly.")

        return f"M3 S175\n G4 P0.2;\n"  # Turn on the fan + change laser power

# Instantiate a compiler, specifying the custom interface and the speed at which the tool should move.
gcode_compiler = Compiler(CustomInterface, movement_speed=1000, cutting_speed=300, pass_depth=5)

curves = parse_file("/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Images/resized_Simple_light_bulb_graphic.svg") # Parse an svg file into geometric curves

gcode_compiler.append_curves(curves) 
gcode_compiler.compile_to_file("drawing.gcode")