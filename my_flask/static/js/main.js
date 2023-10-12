


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
	buildVolume: { x: 280, y: 210, z: 150 },
	initialCameraPosition: [0, 400, 450],
	//debug: true,
	allowDragNDrop: true,
}));  // draw a diagonal line
preview.renderTravel = true
let gcode = await fetch('/static/Image_Storage/Gcodes/previous.gcode');
gcode = await gcode.text();
console.log(gcode);
preview.processGCode(gcode);



/*	The following code handle the selection of files,
*	if the file is an image it first converts it to
*	gcode and is thus later able to directly send the
*	gcode file to the server.
*/

let gcodeFile; // string
let svgFile; // blob
let imageFile; // blob

document.getElementById('inputfile').addEventListener('change', function () {
	let file = this.files[0];
	let fr = new FileReader();
	if (file.type === "text/x.gcode" || file.type === "") {
		fr.onload = function () {
			let result = fr.result;
			gcodeFile = fr.result;
			preview.processGCode(result);
			handleGcodeFile();

		}
		fr.readAsText(file);
	} else if (
		file.type === "image/jpeg" ||
		file.type === "image/bmp" ||
		file.type === "image/png"
	) {
		fr.onload = function () {
			let result = fr.result;

			const img = document.createElement('img');
			img.src = result;

			img.onload = async function () {
				const canvas = document.createElement("canvas");
				const ctx = canvas.getContext("2d");
				var val = document.getElementById('Size').value;
				if (val == "small") {
					canvas.width = 200;
					canvas.height = 200;
				} else if (val == "medium") {
					canvas.width = 400;
					canvas.height = 300;
				} else if (val == "large") {
					canvas.width = 800;
					canvas.height = 600;
				}
				ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
				const dataURI = canvas.toDataURL();
				document.querySelector('img').src = dataURI;

				const res = await fetch(dataURI);
				imageFile = await res.blob();
				imageFile = new File([imageFile], file.name)
				handleImageFile();
			}
		}
		fr.readAsDataURL(file);
	}
});


function handleGcodeFile() {

	// Add functionality to send gcode to server
	console.log(gcodeFile);

	// Send 'gcodeFile' to backend
}

function handleSvgFile() {
	// Add functionality to convert svg to gcode and then handle
	console.log(svgFile);
	// gcodeFile = <DO CONVERSION>
	//
	// Possibly use svg2gcode library - wasm
	handleGcodeFile();
}

function handleImageFile() {
	// Add functionality to convert to svg and then handle

	console.log(imageFile);


	const formData = new FormData();
	formData.append("file1", imageFile);
	formData.append("submit_button", "upload_image")

	const request = new XMLHttpRequest();
	request.open("POST", "/");
	request.send(formData);

	// svgFile = <DO CONVERSION>
	//
	// Possibly use bitmap2vector library - javascript
	handleSvgFile()

	// setTimeout(function(){
	// 	location.replace(location.href);
	// }, 3000);

}
