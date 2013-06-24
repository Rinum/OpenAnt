Prime.prototype.load = function(){	
	//Create initial controllers
	var controllers = [];
	
	controllers.push(new FPSController(this));
	
	for(var i in controllers){
		this.add_controller(controllers[i]);
	}
	
	this.Socket = new Socket();
};