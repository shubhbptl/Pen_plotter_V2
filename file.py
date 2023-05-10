old_filename = "/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Gcodes/drawing.gcode"
num_lines = 1  
top_string = """G92 X0 Y0;\n"""
bottom_string = """G1 X0 Y0;\n"""
with open(old_filename, 'r') as f:
    old_data = f.readlines()

    new_data = old_data[:num_lines] + [top_string] + old_data[num_lines:]
            
    #new_data = old_data[:num_lines] + ["""G92 X0 Y0;\n"""] + old_data[num_lines:]
   # new_string = """Hello how are you\nMS 0420l;\nwodjao;\n""" + old_data
           
with open(old_filename,'w') as f:
    f.writelines(new_data + old_data[num_lines:])

with open(old_filename, 'a') as f:
    f.write(bottom_string)
    