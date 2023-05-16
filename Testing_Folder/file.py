old_filename = "/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Gcodes/drawing.gcode"
logo_filename = "/home/penplotter/Pen_plotter_V2/mvths engineering (2).gcode"
num_lines = 1  
top_string = """G92 X0 Y0;\n"""
bottom_string = """G1 X0 Y0;\n"""
with open(old_filename, 'r') as f:
    old_data = f.readlines()

    new_data = old_data[:num_lines] + [top_string] + old_data[num_lines:]
           
with open(old_filename,'w') as f:
    f.writelines(new_data + old_data[num_lines:])

with open(old_filename, 'a') as f:
    f.write(logo_filename + bottom_string)
    