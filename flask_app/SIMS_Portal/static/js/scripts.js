window.setTimeout(function() {
	$("#alert").fadeTo(500, 0) 
}, 6000);

var scrollSpy = new bootstrap.ScrollSpy(document.body, {
  target: '#navbar-example'
})