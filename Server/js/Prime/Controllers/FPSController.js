FPSController = function(parent){
	this.parent = parent;
	this.init();
};

FPSController.prototype.init = function(){
	//Set controller viewport
	this.viewport = this.parent.viewport;

	//Create FPS Object to display FPS on screen
	this.fps_object = new FPS(this);
	
	//Add object to Prime
	this.fps_object_id = this.parent.add_object(this.fps_object);
	
	//Initial logic
	this.interval = 2000; //show avg fps for past 2 seconds
	this.last_time = null;
	this.frames = 0;
};

FPSController.prototype.run = function(time){
	if(!this.last_time)
		this.last_time = this.parent.run_time;

	var diff = time.diff(this.last_time);

	if(diff >= this.interval){
		this.fps_object.fps = Math.round(1000 * this.frames/diff);
		this.last_time = time;
		this.frames = 0;
	}
	
	this.frames++;
};