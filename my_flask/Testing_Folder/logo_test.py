old_filename = "/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Gcodes/previous.gcode"
logo_filename = "/home/penplotter/Pen_plotter_V2/my_flask/Testing_Folder/mvths engineering (2).gcode"

with open(logo_filename, 'r') as f:
    data = f.read()
    f.close()

with open(old_filename, 'r') as f:
    old_data = f.read()
    f.close()

with open(old_filename, 'w') as f:
    f.write(data)
    f.write(old_data)
    f.close()
