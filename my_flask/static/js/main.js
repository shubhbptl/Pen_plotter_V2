


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
	allowDragNDrop: true,
}));  // draw a diagonal line
preview.renderTravel = true
const gcode = ''; 
preview.processGCode(gcode);



/*	The following code handle the selection of files,
*	if the file is an image it first converts it to 
*	gcode and is thus later able to directly send the
*	gcode file to the server.
*/

let gcodeFile;
let svgFile;
let imageFile;

document.getElementById('inputfile').addEventListener('change', function() {
	let file = this.files[0];
	let fr = new FileReader();
	if(file.type === "text/x.gcode" || file.type === ""){
		fr.onload = function(){
			let result = fr.result;
			gcodeFile = fr.result;
			preview.processGCode(result);
			handleGcodeFile();
		}
		fr.readAsText(file);
	}else if(
		file.type === "image/jpeg" ||
		file.type === "image/bmp" ||
		file.type === "image/png"
	){
		fr.onload = function(){
			let result = fr.result;

			const img = document.createElement('img');	
			img.src = result;

			img.onload = async function(){
				const canvas = document.createElement("canvas");
				const ctx = canvas.getContext("2d");

				canvas.width = 200;
				canvas.height = 150;

				ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
				const dataURI = canvas.toDataURL();
				document.querySelector('img').src = dataURI;

				const res = await fetch(dataURI);
				imageFile = await res.blob();
				handleImageFile();
			}
		}
		fr.readAsDataURL(file);
	}
});


function handleGcodeFile(){
	// Add functionality to send gcode to server
	console.log(gcodeFile);

	// Send 'gcodeFile' to backend
}

function handleSvgFile(){
	// Add functionality to convert svg to gcode and then handle
	
	console.log(svgFile);
	// gcodeFile = <DO CONVERSION>
	//
	// Possibly use svg2gcode library - wasm
	handleGcodeFile();
}

function handleImageFile(){
	// Add functionality to convert to svg and then handle

	console.log(imageFile);
	// svgFile = <DO CONVERSION>
	// 
	// Possibly use bitmap2vector library - javascript
	handleSvgFile()
}
