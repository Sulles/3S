/* =============================================================
		INITIALIZING GLOBAL VARIABLES AND FUNCTIONS
==============================================================*/
// Colors
/*
COLORS = {	'LIGHTGRAY': 	'rgb(175, 175, 175)',
			'GRAY': 		'rgb(100, 100, 100)',
			'DARKGRAY': 	'rgb( 50,  50,  50)',
			'BLACK': 		'rgb(  0,   0,   0)',
			'NAVYBLUE': 	'rgb( 60,  60, 100)',
			'WHITE': 		'rgb(255, 255, 255)',
			'WHITERED': 	'rgb(255, 230, 230)',
			'RED': 			'rgb(255,   0,   0)',
			'REDBROWN': 	'rgb( 89,   0,   0)',
			'PALERED': 		'rgb(255,  75,  75)',
			'GREEN': 		'rgb(  0, 255,   0)',
			'BLUE': 		'rgb(  0,   0, 255)',
			'PALEBLUE': 	'rgb( 75,  75, 255)',
			'YELLOW': 		'rgb(255, 255,   0)',
			'PALEYELLOW': 	'rgb(255, 255, 175)',
			'ORANGE': 		'rgb(255, 128,   0)',
			'PHOBOSCLR': 	'rgb(222, 184, 135)',
			'DEIMOSCLR': 	'rgb(255, 222, 173)',
			'BROWN': 		'rgb(255, 240, 220)',
			'DARKBROWN': 	'rgb( 75,  75, 255)',
			'BGCOLOR': 		'rgb(  0,   0,   0)'}
*/
// Server Connection
var Connection = new WebSocket('ws://localhost:6789/');
// Bodies and Players
var ALL_BODIES = [];
var ALL_PLAYERS = [];
// Game State and Reticle Globals
var GAME_STATE = null;
var RETICLE = null;
// Buttons
var Buttons = {map: false, engi:false};
// UI vars
var center_w = 0; // will be updated in main()
var center_h = 0; // will be updated in main()
REFRESH_RATE = 10; 	// in ms
// Main screen width and height
screen_w = 1000;
screen_h = 600;
// System screen width and height
system_screen_w = 450;
system_screen_h = 450;
system_screen_h_offset = -50;
// Radians stuff
ToRad = Math.PI/180;
ToDeg = 180/Math.PI;
// For Colors
function array2para(array){
	return 'rgb(' + array[0] + ',' + array[1] + ',' + array[2] + ')';
}
// CREATING VECTORS AND THEIR MATH
vec2d = function(x, y) {
	this.x = x;
	this.y = y;
	// Magnitude of Vector
	this.mag = Math.sqrt(Math.abs(this.x*this.x + this.y*this.y));
	// Angle of Vector from Origin
	this.theta = Math.atan2(this.y, this.x) * ToDeg;
}
// Unit Vector
vec2d.prototype.unit = function() {
	return new vec2d(this.x/this.mag, this.y/this.mag);
}
// Vector addition
vec2d.prototype.addVec = function(vec) {
	return new vec2d(this.x + vec.x, this.y + vec.y);
}
// Vector subtraction
vec2d.prototype.subVec = function(vec) {
	return new vec2d(this.x - vec.x, this.y - vec.y);
}
// Subtract by a Number
vec2d.prototype.subNum = function(num) {
	return new vec2d(this.x - num, this.y - num);
}
// Add by a Number
vec2d.prototype.addNum = function(num) {
	return new vec2d(this.x + num, this.y + num);
}
// Multiply by non-vector
vec2d.prototype.mult = function(num) {
	return new vec2d(this.x*num, this.y*num);
}
// Divide by non-vector
vec2d.prototype.div = function(num) {
	return new vec2d(this.x/num, this.y/num);
}
// Vector dot product
vec2d.prototype.dot = function(vec) {
	return this.x*vec.x + this.y*vec.y;
}
// Vector cross product
vec2d.prototype.cross = function(vec) {
	return this.x*vec.y - this.y*vec.x;
}
// Distance between two Vectors
vec2d.prototype.dist = function(vec) {
	var xsqr = Math.abs((this.x-vec.x)*(this.x-vec.x));
	var ysqr = Math.abs((this.y-vec.y)*(this.y-vec.y));
	return Math.sqrt(xsqr + ysqr)
}
// Rotate about a point
vec2d.prototype.rotateAbout = function(origin, angle) {
	// https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
	angle *= ToRad;
	qx = origin.x + Math.cos(angle)*(this.x - origin.x) - Math.sin(angle)*(this.y - origin.y);
	qy = origin.y + Math.sin(angle)*(this.x - origin.x) + Math.cos(angle)*(this.y - origin.y);
	return new vec2d(qx, qy);
}


/* =============================================================
					SERVER FUNCTIONS
==============================================================*/

/* LINK TO SERVER, handles...
	- Connection Errors
	- Closed Connection
	- Receiving and Handling Messages
*/
function link2server() {
	// Log errors
	Connection.onerror = function (error) {
		console.log('WebSocket Error ' + error);
	};
	// On close
	Connection.onclose = function () {
		document.getElementById("numOfUsers").innerHTML = "ERROR: Connection to server lost...";
	}

	// Log messages from the server
	Connection.onmessage = function (message) {
		//console.log('Server: ' + message.data);
		data = JSON.parse(message.data);
		//sleep(50);
		switch (data.type) {
			// Depending on Type of message, switch through appropriate action
			case 'ping':
				send_pong();
				break;
			case 'message':
				console.log(data.txt)
				document.getElementById("out").innerHTML = data.txt+" \n";
				break;
			case 'users':
				var usertext = (data.count.toString() + " user" + (data.count == 1 ? "" : "s"));
				document.getElementById("numOfUsers").innerHTML = usertext;
				break;
			case 'body':
				//console.log(data)
				addBody(data);
				document.getElementById("body_out").innerHTML += "| " + data.Name + " |";
				break;
			case 'start_timer':
				clock = window.setInterval(runTimer, INTERVAL_TIMER);
				break;
			case 'stop_timer':
				window.clearInterval(clock);
				break;
			case 'pulse_delay':
				console.log("clock is being delayed by " + data.delay)
				window.clearInterval(clock);
				sleep(data.delay*250);
				clock = window.setInterval(runTimer, INTERVAL_TIMER);
				break;
			default:
				console.log("unsupported event", data);
		}
	};
}


// SEND MESSAGE TO SERVER FUNCTIONS

function send_space() {
	Connection.send(JSON.stringify({action: 'space'}));
}
function send_start_game() {
	Connection.send(JSON.stringify({action: 'start_game'}));
}
function runTimer() {
	console.log("Pulse Sent")
	Connection.send(JSON.stringify({action: 'pulse'}));
}
function send_start_timer() {
	Connection.send(JSON.stringify({action: 'start_timer'}));
}
function send_stop_timer() {
	Connection.send(JSON.stringify({action: 'stop_timer'}));
}
function send_start_ping() {
	Connection.send(JSON.stringify({action: 'send_ping'}));
}
function send_pong() {
	Connection.send(JSON.stringify({action: 'pong'}));
}


// SLEEP FOR DELAY AND TEST PURPOSES

function sleep(msec){
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++){
		if (new Date().getTime() - start > msec){
			break;
		}
	}
}

/* =============================================================
			USER INTERFACE AND OTHER DRAWING
==============================================================*/

/* CREATE UI, handles... 
	- Filling background with black
	- Drawing main UI background
	- Drawing buttons
	- Creating System Draw Board background
*/
function createUI(ctx) {
	fillBackground(ctx, 'rgb(15,15,15)');
	draw_ui_background(ctx, 'rgb(100,100,100)');
	draw_map_butt(ctx, false);
	draw_engi_butt(ctx, false);
	draw_SystemDrawBoardBackground(ctx);
}

// UI AND BACKGROUNDS

function fillBackground(ctx, color) {
	ctx.fillStyle = color;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}
function draw_SystemDrawBoardBackground(ctx){
	ctx.strokeStyle = 'rgb(255, 255, 255';
	ctx.strokeRect(center_w - system_screen_w/2 - 1, center_h - system_screen_h/2 - 1 + system_screen_h_offset, system_screen_w + 2,system_screen_h + 2);
}
function draw_ui_background(ctx) {
	grey = 'rgb(100, 100, 100)';
	ctx.strokeStyle = 'rgb(66,170,244)';
	ctx.strokeRect(center_w - screen_w/2, center_h - screen_h/2, screen_w,screen_h);
	ctx.strokeStyle = 'rgb(255,255,255)';
	ctx.strokeRect(center_w - screen_w/2 - 2, center_h - screen_h/2 -2, screen_w + 4, screen_h + 4);
  	// begin left ui-holder
  	ctx.strokeStyle = grey;	
  	var point = [center_w - screen_w/2, center_h + screen_h/4.5];
  	ctx.beginPath();
  	ctx.moveTo(point[0], point[1]);
  	ctx.bezierCurveTo(point[0], point[1] + 10, point[0], point[1] + 20, point[0] + 25, point[1] + 25);
  	point[0] += 25; point[1] += 25;
  	ctx.lineTo(point[0] + 225, point[1] + 45);
  	point[0] += 225; point[1] += 45;
  	ctx.bezierCurveTo(point[0] + 25, point[1] + 5, point[0] + 50, point[1] + 10, point[0] + 50, point[1] + 35);
  	point[0] += 50; point[1] += 25;
  	ctx.lineTo(point[0], center_h + screen_h/2);
  	ctx.lineTo(center_w - screen_w/2, center_h + screen_h/2);
  	ctx.closePath();
  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();
  	// begin right ui-holder
  	point = [center_w + screen_w/2, center_h + screen_h/4.5];
  	ctx.beginPath();
  	ctx.moveTo(point[0], point[1]);
  	ctx.bezierCurveTo(point[0], point[1] + 10, point[0], point[1] + 20, point[0] - 25, point[1] + 25);
  	point[0] -= 25; point[1] += 25;
  	ctx.lineTo(point[0] - 225, point[1] + 45);
  	point[0] -= 225; point[1] += 45;
  	ctx.bezierCurveTo(point[0] - 25, point[1] + 5, point[0] - 50, point[1] + 10, point[0] - 50, point[1] + 35);
  	point[0] -= 50; point[1] += 25;
  	ctx.lineTo(point[0], center_h + screen_h/2);
  	ctx.lineTo(center_w + screen_w/2, center_h + screen_h/2);
  	ctx.closePath();
  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();
}

// BUTTONS

function draw_map_butt(ctx, active) {
	var color = 'rgba(0,0,0,0)';
	if (active) {
		color = 'rgba(255,170,0,0.7)';
	} else {
		color = 'rgba(22,86,142,0.7)';
	}
	ctx.beginPath();
	ctx.moveTo(center_w - 210, center_h + 254);
	ctx.strokeStyle = 'black';
	ctx.fillStyle = color;
	ctx.arc(center_w - 250, center_h + 254, 40, 0, Math.PI*2);
	ctx.stroke();
	ctx.fill();
	ctx.closePath();
	ctx.strokeStyle = 'white';
	for (x = 2; x < 5; x++) {
		ctx.beginPath();
		ctx.arc(center_w - 250, center_h + 254, x*8, 0, Math.PI*2);
		ctx.closePath();
		ctx.stroke();
	}
	ctx.beginPath();
	ctx.fillStyle = 'white';
	ctx.arc(center_w - 250, center_h + 254, 10, 0, Math.PI*2);
	ctx.arc(center_w - 250 + 16, center_h + 254 - 18, 3, 0, Math.PI*2);
	ctx.fill();
	ctx.closePath();
	ctx.beginPath();
	ctx.arc(center_w - 250 - 30, center_h + 254 + 13, 5, 0, Math.PI*2);
	ctx.arc(center_w - 250, center_h + 254 + 16, 2, 0, Math.PI*2);
	ctx.fill();
	ctx.closePath();
}
function draw_engi_butt(ctx, active) {
	var img = new Image();
	img.onload = function() {
		ctx.drawImage(img, center_w - 350, center_h + 222, 40, 40);
	}
	img.src = 'gear.png';

	var color = 'rgba(0,0,0,0)';
	if (active) {
		color = 'rgba(255,170,0,0.7)';
	} else {
		color = 'rgba(22,86,142,0.7)';
	}
	ctx.beginPath();
	ctx.strokeStyle = 'black';
	ctx.fillStyle = color;
	ctx.arc(center_w - 315, center_h + 280, 10, 0, Math.PI/2);
	ctx.lineTo(center_w - 345, center_h + 290);
	ctx.arc(center_w - 345, center_h + 280, 10, Math.PI/2, Math.PI);
	ctx.lineTo(center_w - 355, center_h + 215);
	ctx.arc(center_w - 345, center_h + 215, 10, Math.PI, Math.PI*3/2);
	ctx.lineTo(center_w - 315, center_h + 205);
	ctx.arc(center_w - 315, center_h + 215, 10, Math.PI*3/2, Math.PI*2);
	ctx.closePath();
	ctx.stroke();
	ctx.fill();
}
function unactivate_butts(ctx) {
	draw_behind_butts(ctx);
	draw_map_butt(ctx, false);
	draw_engi_butt(ctx, false);
}
function draw_behind_butts(ctx) {
	ctx.strokeStyle = 'rgb(175, 175, 175)';
	offset = 5; //pixels
	var point = [center_w - screen_w/2, center_h + screen_h/4];
	ctx.moveTo(point[0], point[1]);
	ctx.beginPath();
	ctx.lineTo(point[0] + offset, point[1] + offset);
	ctx.lineTo(point[0] + 285 + offset, point[1] + 75 - offset);
	point[0] += 285; point[1] += 75;
	ctx.lineTo(point[0] + offset, center_h + screen_h/2 - offset);
	ctx.lineTo(center_w - screen_w/2 + offset, center_h + screen_h/2 - offset);
	ctx.closePath();
  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();
}

// RETICLE

var Reticle = function(){
	this.center = new vec2d(0,0);
	this.radius = 10;
	this.theta = 0;
}
Reticle.prototype.draw = function(ctx) {
	ctx.beginPath();
	ctx.rect(center_w - system_screen_w/2, center_h - system_screen_h/2 + system_screen_h_offset, system_screen_w, system_screen_h);
	ctx.stroke(); ctx.closePath(); ctx.clip();

	var scrnXY = vec2Screen(this.center);
	var screenXY = new vec2d(scrnXY[0], scrnXY[1]);
	rotate_ctx(ctx, this.theta);
	screenXY = screenXY.rotateAbout( new vec2d(0,0), -this.theta);
	ctx.beginPath();
	ctx.strokeStyle = 'rgb(255,255,255)';
	ctx.arc(screenXY.x, screenXY.y, this.radius*Math.sqrt(1.5), 0, 2*Math.PI);
	ctx.rect(screenXY.x - this.radius, screenXY.y - this.radius, 2*this.radius, 2*this.radius);
	ctx.stroke();
	ctx.closePath();
	unrotate_ctx(ctx, this.theta);
	//console.log("reticle should be showing...")
	this.theta += 1/50 * (REFRESH_RATE);
}
Reticle.prototype.newFocus = function() {
	this.center = (GAME_STATE.FocusBody.Position.subVec(GAME_STATE.Focus)).mult(GAME_STATE.KM2PIX);
	this.radius = (GAME_STATE.FocusBody.Diameter/2)*GAME_STATE.KM2PIX;
	this.theta = 0;
}

// CTX MODIFIERS

function rotate_ctx(ctx, deg) {
	ctx.save();
	ctx.rotate(deg*ToRad);
}
function unrotate_ctx(ctx, deg) {
	ctx.rotate(-deg*ToRad);
	ctx.restore();
}



// MISCELLANEOUS: ON CLICK FUNCTION

function onClick(event) {
    var pos = new vec2d(event.clientX, event.clientY);
    var coords = "X coords: " + pos.x + ", Y coords: " + pos.y;
    document.getElementById("demo").innerHTML = coords;
	//var bleep = new Audio();
    //bleep.src = "dustyroom_multimedia_positve_correct_complete_ping.mp3";
    if (!Buttons.map && pos.dist(new vec2d(center_w - 240, center_h + 260)) < 40) {
    	Buttons.map = true;
    	Buttons.engi = false;
    	unactivate_butts(ctx);
    	draw_map_butt(ctx, true);
	    //bleep.play();
    }
    else if (!Buttons.engi && center_w-350<pos.x && pos.x<center_w-300 && center_h+213<pos.y && pos.y<center_h+300) {
    	Buttons.engi = true;
    	Buttons.map = false;
    	unactivate_butts(ctx);
    	draw_engi_butt(ctx, true);
	    //bleep.play();
    }
}



/* =============================================================
						GAME STATE
==============================================================*/

/* GAME STATE, handles...
	- Current Focus Object Index
	- Scale/Zoom via KM2PIX
	- Changing Focus
	- Generating Focus UI arrays
*/

GameState = function() {
	this.FocusBody = null;
	this.Focus = new vec2d(0,0);
	this.KM2PIX = 1/100;
	this.FocusUI_topLevel = [''];
	this.FocusUI_currentLevel = [''];
	this.FocusUI_bottomLevel = [''];
}
GameState.prototype.changeFocusBody = function(newFocusIndex){
	this.FocusBody = ALL_BODIES[newFocusIndex];
	if (this.FocusBody.Parent != null) {
		this.FocusUI_topLevel = this.FocusBody.Parent.Name;
		this.FocusUI_currentLevel = [];
		for (x in this.FocusBody.Parent.Children.length){
			this.FocusUI_currentLevel.push(this.FocusBody.Parent.Children[x].Name);
		}
	}
	else { 
		this.FocusUI_topLevel = [''];
		this.FocusUI_currentLevel = [this.FocusBody.Name];
	}
	if (this.FocusBody.Children.length > 0){
		this.FocusUI_bottomLevel = [];
		for (x in this.FocusBody.Children){
			this.FocusUI_bottomLevel.push(this.FocusBody.Children[x].Name);
		}
	}
	else {
		this.FocusUI_bottomLevel = [''];
	}
}
GameState.prototype.updateFocus = function() {
	this.Focus = this.FocusBody.Position;
}



/* =============================================================
					BODIES AND PLAYERS
==============================================================*/

/* MAIN BODY CLASS, handles...
	- Initialization
	- Adding parent
	- Adding child
*/

Body = function(data, indx) {
	this.Name = data.Name;
	this.Diameter = data.Diameter;
	this.Position = new vec2d(data.Position[0], data.Position[1]);
	this.Velocity = new vec2d(data.Velocity[0], data.Velocity[1]);
	if (data.e != null && data.e.length > 1) { this.e = new vec2d(data.e[0], data.e[1]); }
	else { this.e = data.e; }
	this.isCircular = data.isCircular;
	this.a = data.a;
	this.b = data.b;
	this.A = data.A;
	this.dAdt = data.dAdt;
	this.Children = [];
	this.Color = data.Color;
	this.indx = ALL_BODIES.length;
}
Body.prototype.addParent = function(parent) {
	for (x in ALL_BODIES){
		if (ALL_BODIES[x].Name == parent){
			this.Parent = ALL_BODIES[x];
			this.Parent.addChild(this);
		}
	}
}
Body.prototype.addChild = function(child) {
	this.Children.push(child);
}

// Adds Body from Server Data
function addBody(data) {
	ALL_BODIES.push(new Body(data));
	if (data.Parent != null){
		ALL_BODIES[ALL_BODIES.length-1].addParent(data.Parent);
	}
}


/* =============================================================
					BODY AND PLAYER DRAWING 
==============================================================*/
function clear_System_Canvas(ctx) {
	ctx.fillStyle = 'rgb(0, 0, 0';
	ctx.fillRect(center_w - system_screen_w/2, center_h - system_screen_h/2 + system_screen_h_offset, system_screen_w,system_screen_h);
}

/* UPDATE SYSTEM DRAW BOARD, handles...
	- Checking if Body is within System Draw Board bounds
	- Sends info to draw function
*/

function update_System_Canvas(ctx) {
	if (ALL_BODIES.length > 0){
		for (x in ALL_BODIES){
			// FOCUS AND KM2PIX IS NOT UNIFORM
			middle_of_body = (ALL_BODIES[x].Position.subVec(GAME_STATE.Focus)).mult(GAME_STATE.KM2PIX);
			dia = ALL_BODIES[x].Diameter*GAME_STATE.KM2PIX;
			CheckXAxis1 = -(system_screen_w + dia)/2 < middle_of_body.x;
			CheckXAxis2 = middle_of_body.x < (system_screen_w + ALL_BODIES[x].Diameter*GAME_STATE.KM2PIX)/2;
			CheckYAxis1 = -(system_screen_h + ALL_BODIES[x].Diameter*GAME_STATE.KM2PIX)/2 < middle_of_body.y; 
			CheckYAxis2 = middle_of_body.y < (system_screen_h + ALL_BODIES[x].Diameter*GAME_STATE.KM2PIX)/2;
			if (CheckXAxis1 && CheckXAxis2 && CheckYAxis1 && CheckYAxis2){
				console.log("Showing: " + ALL_BODIES[x].Name + " Position is: " + middle_of_body.x + ", " +middle_of_body.y);
				draw_body(ctx, ALL_BODIES[x], dia, middle_of_body);
			}
		}
	}
	else { console.log("ERROR: No Bodies to Display"); }
}
function draw_body(ctx, body, dia, middle_of_body) {
	//ctx.moveTo(middle_of_body.x, middle_of_body.y);
	color = array2para(body.Color);
	ctx.beginPath();
	ctx.rect(center_w - system_screen_w/2, center_h - system_screen_h/2 + system_screen_h_offset, system_screen_w, system_screen_h);
	ctx.stroke(); ctx.closePath(); ctx.clip();
	ctx.beginPath();
	screenXY = vec2Screen(middle_of_body);
	ctx.fillStyle = color;
	ctx.arc(screenXY[0], screenXY[1], dia/2, 0, 2*Math.PI);
	ctx.fill(); ctx.closePath();
}
function vec2Screen(vec) {
	return [center_w + vec.x, center_h + vec.y + system_screen_h_offset];
}
//return [int(MiddlePoint[0] + SURF_WIDTH/2),int(SURF_HEIGHT/2 - MiddlePoint[1])]




/* =============================================================
		FUNCTIONS CALLED FROM HTML and MAIN GAME LOOP
==============================================================*/

/* MAIN GAME LOOP, handles...
	- Getting input
	- Handling input
	- Clear and Update System Draw Board
	- Reticle
*/

function mainLoop() {
	ctx = document.getElementById('canvas').getContext('2d');
	//var input = check4Input();
	//handleInput(input);
	clear_System_Canvas(ctx);
	update_System_Canvas(ctx);

	if (ALL_BODIES.length > 0 && GAME_STATE.FocusBody == null) {
		GAME_STATE.changeFocusBody(5);
		GAME_STATE.updateFocus();
		RETICLE.newFocus();
	}
	if (GAME_STATE.FocusBody != null) {
		RETICLE.draw(ctx);
	}

	//console.log('updated...')
}

/* MAIN FUNCTION CALLED FROM HTML, handles...
	- Creating UI
	- Calling mainLoop function iteratively every 10ms
	- Establishing link to server
*/

function main() {
	// Canvas vars
	canvas = document.getElementById('canvas');
	ctx = canvas.getContext('2d');
	canvas.width = window.innerWidth - 20;
	canvas.height = window.innerHeight - 30;
	center_w = canvas.width/2 - 5;
	center_h = canvas.height/2;

	createUI(ctx);
	link2server();
	GAME_STATE = new GameState();
	RETICLE = new Reticle();
	//console.log(GAME_STATE.KM2PIX);
	setInterval(mainLoop, REFRESH_RATE);

	/* TRIAL CODE 
	var v = new vec2d(1,2);
	var v2 = new vec2d(2,3);
	console.log(v);
	console.log(v2);
	console.log(v.mult(2));
	//v2_ = v2.unit();
	//console.log(v2);
	//v2.addNum(1)
	//console.log(v2);
	//console.log(v2_);
	*/
}