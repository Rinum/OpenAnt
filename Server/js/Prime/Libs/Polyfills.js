(function() {
	var lastTime = 0;
	var vendors = ['ms', 'moz', 'webkit', 'o'];
	for(var x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
		window.requestAnimationFrame = window[vendors[x]+'RequestAnimationFrame'];
		window.cancelAnimationFrame = window[vendors[x]+'CancelAnimationFrame'] 
					   || window[vendors[x]+'CancelRequestAnimationFrame'];
	}

	if (!window.requestAnimationFrame){
		window.requestAnimationFrame = function(callback, element) {
			var currTime = new Date().getTime();
			var timeToCall = Math.max(0, 16 - (currTime - lastTime));
			var id = window.setTimeout(function(){callback(currTime + timeToCall); }, timeToCall);
			lastTime = currTime + timeToCall;
			return id;
		};
	}

	if (!window.cancelAnimationFrame){
		window.cancelAnimationFrame = function(id){
			clearTimeout(id);
		};
	}
}());

extend = function() {
	// copy reference to target object
	var target = arguments[0] || {}, a = 1, al = arguments.length, deep = false;

	// Handle a deep copy situation
	if (target.constructor == Boolean) {
		deep = target;
		target = arguments[1] || {};
	}

	var prop;

	for (var a = 0; a < al; a++){
		// Only deal with non-null/undefined values
		if ((prop = arguments[a]) != null){
			// Extend the base object
			for (var i in prop) {
				// Prevent never-ending loop
				if (target == prop[i]) continue;

				// Recurse if we're merging object values
				if (deep && typeof prop[i] == 'object' && target[i]) {
					jQuery.extend(target[i], prop[i]);
				} else if (prop[i] != 'undefined'){
					target[i] = prop[i];
				}
			}
		}
	}

	// Return the modified object
	return target;
};