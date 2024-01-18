from pyhershey import glyph_factory
from pyhershey.show import show_glyph

a = glyph_factory.from_ascii('a', 'roman_simplex')
print(a)
text = "/home/penplotter/Pen_plotter_V2/my_flask/text.txt"
f = open(text,"w")
f.write(a)
f.close()
