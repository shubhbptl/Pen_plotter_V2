import re
import math

output_file = "text_v2.gcode"
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
        gcode)  # Write modified G-code to output file
        with open(output_file, "w") as f:
            f.write(new_gcode) 
            # Example usage:
            
input_file = "test.gcode"
output_file = "test_v2.gcode"
angle = 180  # Convert angle to radians if needed
process_gcode(input_file, output_file, angle)
