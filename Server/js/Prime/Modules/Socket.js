Socket = function(options){
	var This = this;
	
	var defaults = {
		host: window.location.hostname !== 'localhost' ? 'ws.' + window.location.hostname : 'localhost',
		connect: function() {
			This.session.on('event',function(data){
				console.log(data);
			});

			This.session.on('disconnect', function(){
				console.log('Disconnected :(');
			});
		}
	};
	
	this.options = extend(true,defaults,options);
	
	this.init();
};

Socket.prototype.init = function(){
	var session = io.connect(this.options.host);
	session.on('connect', this.options.connect);
	
	this.session = session;
};