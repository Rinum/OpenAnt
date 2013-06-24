FPS = function(controller){
	this.controller = controller;	
	this.init();
};

FPS.prototype.init = function(){
	//Initialize vars
	this.fps = 0;
	
	//Create Canvas
	this.canvas = document.createElement('canvas');
	this.canvas.height = 8;
	this.canvas.width = 35;
	this.canvas.style.position = 'absolute';
	this.canvas.style.left = '5px';
	this.canvas.style.bottom = '5px';
	this.context = this.canvas.getContext('2d');
	
	//Place canvas on controller's viewport
	this.controller.viewport.appendChild(this.canvas);
};

FPS.prototype.render = function(time){
	var canvas = this.canvas;
	var context = this.context;
	context.fillStyle = "#000000";
	context.font = "8pt Arial";
	context.clearRect(0,0,canvas.width,canvas.height);
	context.fillText(this.fps + " FPS", 0, 8);
};