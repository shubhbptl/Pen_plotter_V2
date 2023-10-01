


const marked = window.marked;
console.log(marked);
const request = new Request(
	"/static/markdown.md",
	{}
);
const response = await fetch(request);
const markdown = await response.text();
const html = marked.parse(markdown);
document.querySelector('#markdown').innerHTML = html;

const preview = (window.preview = new GCodePreview.init({
	canvas: document.querySelector('canvas'),
	lineWidth: 4,
	buildVolume: {x: 150, y: 150, z: 150},
	initialCameraPosition: [0,400,450],
	//debug: true,
	allowDragNDrop: false,
}));  // draw a diagonal line
preview.renderTravel = true
const gcode = ''; 
preview.processGCode(gcode);



document.getElementById('inputfile')
            .addEventListener('change', function() {
              
            var fr=new FileReader();
            fr.onload=function(){
		preview.processGCode(fr.result);	    
	    }
              
            fr.readAsText(this.files[0]);
		
});
