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
