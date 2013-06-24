/*
 * Object Class
 * Interactive stuff
 * 
 * Object.position = {
 *	x: 120,
 *	y: 513,
 *	z: 1
 * };
 * 
 * Object.state = {
 *	id: 'rest', //what state is the object in?
 *	start: 0 //when the state started
 * };
 * 
 * Object.states = {
 *	'rest':{
 *		map: null,
 *		events:{
 *			click: {
 *				Object: function(){
 *					//Do something
 *				}
 *			}
 *		},
 *		render: function(start, timeAtRender){
 *			//draw object
 *		}
 *	}
 * };
 *
 * //global state settings...not needed if defined at the individual state level
 * Object.defaults = {
 *	dimensions:{
 *		width: 100,
 *		height: 100,
 *		scale: 2
 *	},
 *	//Not necessary to define map... it's there if you need finer control
 *	//In this example each block represents a 20px x 20px area
 *	map:[ //at scale = 1
 *		[0,0,0,0,0],
 *		[0,0,1,0,0],
 *		[0,1,1,[0,1],0],
 *		[0,P,1,0,0],
 *		[0,0,0,0,0]
 *	],
 *	events:{
 *		click: {
 *			1: function(){
 *				//Do something
 *			},
 *			P: function(){
 *				//Do something
 *			}
 *		}
 *	}
 * }
 */

Prime.Object = function(parent,data){
	this.parent = parent;
	this.data = data;	
	this.init();
}

Prime.Object.prototype.init = function(){
	//Parse data
	var data = this.data;
	this.defaults = data.defaults || {};
	this.position = data.position;
	this.state = data.state;
	this.states = data.states;
	
	//Create Canvas
	this.canvas = document.createElement('canvas');
	this.canvas.height = this.defaults.dimensions.height;
	this.canvas.width = this.defaults.dimensions.width;
	this.canvas.style.position = 'absolute';
	this.canvas.style.left = 0;
	this.context = this.canvas.getContext('2d');
	this.parent.viewport.appendChild(this.canvas);
}

Prime.Object.prototype.render = function(time){

}