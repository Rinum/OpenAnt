/*
 * Prime Class
 */
Prime = function(data){
	this.data = data || {};
	this.init();
};

Prime.prototype.init = function(viewport){
	//Time of init
	this.init_time = moment.utc();
	
	//Get the viewport
	if(typeof viewport === 'undefined'){
		this.viewport = document.getElementById('viewport');
	} else {
		this.viewport = viewport;
	}
	
	//Initialize objects container
	this.object_id = 0;
	this.objects = {};
	
	//Initialize controllers container
	this.controller_id = 0;
	this.controllers = {};
	
	//Load initial controllers & objects & modules
	this.load();
	
	//Initialize logic
	this.logic = new Prime.Logic(this);
	
	//Initialize frame
	this.frame = new Prime.Frame(this);
};

Prime.prototype.load = function(){
	//Create initial controllers
	var controllers = [];
	
	controllers.push(new FPSController(this));
	
	for(var i in controllers){
		this.add_controller(controllers[i]);
	}
};

Prime.prototype.run = function(){
	//Now
	var now = moment.utc();
	
	//Time of 1st run
	this.run_time = now;
	
	//Initialize gameloop
	this.gameloop = function(){	
		//Now
		var now = moment.utc();

		this.logic.run(now);
		this.frame.render(now);
		
		requestAnimationFrame(this.gameloop);
	}.bind(this);
	
	this.gameloop_id = requestAnimationFrame(this.gameloop);
};

Prime.prototype.add_controller = function(controller){
	var id = this.controller_id++;
	this.controllers[id] = controller;
	
	return id;
};

Prime.prototype.add_object = function(object){
	var id = this.object_id++;
	this.objects[id] = object;
	
	return id;
};

Prime.prototype.remove_controller = function(id,callback){
	var controller = this.controllers[id];
	
	if(typeof callback == 'undefined')
		callback = controller.stop;
	
	if(controller){		
		//remove controller
		delete this.controllers[id];
		
		//run callback
		if(callback)
			callback();		
	}
};

Prime.prototype.remove_object = function(id,callback){
	var object = this.objects[id];
	
	if(typeof callback == 'undefined')
		callback = object.destroy;
	
	if(object){		
		//remove controller
		delete this.objects[id];
		
		//run callback
		if(callback)
			callback();		
	}
};

Prime.prototype.save = function(){
	window.localStorage.setItem('data',JSON.stringify(this.data));
};

/*
 * Logic Class
 * Solely responsible for running logic functions attached to objects and players
 */
Prime.Logic = function(parent){
	this.parent = parent;
	this.init();
};

Prime.Logic.prototype.init = function(){
};

Prime.Logic.prototype.run = function(time){	
	//Controller logic
	var controllers = this.parent.controllers;
	for(var j in controllers){
		if(controllers[j].run){
			controllers[j].run(time);
		}
	}
};

/*
 * Frame Class
 * Solely responsible for drawing objects on the canvas
 */

Prime.Frame = function(parent){
	this.parent = parent;	
	this.init();
};

Prime.Frame.prototype.init = function(){
	this.viewport = this.parent.viewport;
	this.dimensions = {
		width: this.viewport.width,
		height: this.viewport.height
	};
};

Prime.Frame.prototype.render = function(time){
	//render all objects
	var objects = this.parent.objects;
	for(var i in objects){
		if(objects[i].render){
			objects[i].render(time);
		}
	}
};