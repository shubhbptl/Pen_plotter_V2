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
    // lineWidth: 4,
    buildVolume: {x: 150, y: 150, z: 150},
    initialCameraPosition: [0,400,450],
    // debug: true
    allowDragNDrop: true
  }));  // draw a diagonal line
  const gcode = 'G0 X0 Y0 Z0.2\nG1 X42 Y42 E10';
  preview.processGCode(gcode);
