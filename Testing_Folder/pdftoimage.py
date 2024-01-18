from pdf2image import convert_from_path
 
 
# Store Pdf with convert_from_path function
images = convert_from_path('/home/penplotter/Pen_plotter_V2/my_flask/static/Image_Storage/Text/Report.pdf')
 
for i in range(len(images)):   
      # Save pages as images in the pdf
    images[i].save('page'+ str(i) +'.jpg', 'JPEG')