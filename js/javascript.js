// INITIALIZING BACKGROUND VARS AND STUFF NECESSARY FOR JS TO WORK

var connection = new WebSocket('ws://localhost:6789/');
var ALL_BODIES = []
var butts = {map: false, engi:false};
INTERVAL_TIMER = 3000
function vec_length(vec) {
	return Math.sqrt((vec[0]*vec[0] + vec[1]*vec[1]))
}
function sleep(msec){
	var start = new Date().getTime();
	for (var i = 0; i < 1e7; i++){
		if (new Date().getTime() - start > msec){
			break;
		}
	}
}
function vec(x,y){
	this.x = x;
	this.y = y;
}
vec.prototype.add = function(vec2){
	return vec(this.x+vec2.x, this.y+vec2.y);
}




function createUI(ctx, center_x, center_y){
	screen_x = 1000;
	screen_y = 600;
	system_x = 450;
	system_y = 450;

	bg_color = 'rgb(0,0,0)';
	grey = 'rgb(100, 100, 100)';
	white = 'rgb(255,255,255)';


	fillBackground(ctx, bg_color);

	draw_ui_background(ctx, center_x, center_y, screen_x, screen_y, grey);

	draw_map_butt(ctx, center_x, center_y, false);
	draw_engi_butt(ctx, center_x, center_y, false);

	drawSystemBackground(ctx, center_x, center_y, system_x, system_y);
}

function link2server() {
	// Log errors
	connection.onerror = function (error) {
		console.log('WebSocket Error ' + error);
	};

	// Log messages from the server
	connection.onmessage = function (message) {
		console.log('Server: ' + message.data);
		data = JSON.parse(message.data);
		switch (data.type) {
			/*
			case 'state':
				value.textContent = data.value;
				break;
			*/
			case 'message':
				console.log(data.txt)
				document.getElementById("out").innerHTML = data.txt+"\n";
				break;
			case 'users':
				var usertext = (data.count.toString() + " user" + (data.count == 1 ? "" : "s"));
				document.getElementById("numOfUsers").innerHTML = usertext;
				break;
			case 'body':
				console.log(data)
				document.getElementById("body_out").innerHTML += data.Name + " orbits " + data.Parent + "\n";
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

// ==================================================
// BUTTON FUNCTIONS
function myFunction() {
	connection.send(JSON.stringify({action: 'space'}));
}
function loadSystem() {
	connection.send(JSON.stringify({action: 'start_game'}));
}
function runTimer() {
	console.log("Pulse Sent")
	connection.send(JSON.stringify({action: 'pulse'}));
}
function send_startTimer() {
	connection.send(JSON.stringify({action: 'start_timer'}));
	sleep(2000);
}
function send_stopTimer() {
	connection.send(JSON.stringify({action: 'stop_timer'}));
}


// ==================================================
// DRAW UI FUNCTIONS
function fillBackground(ctx, color) {
	ctx.fillStyle = color;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}
function draw_behind_butts(ctx, center_x, center_y) {
	ctx.strokeStyle = 'rgb(175, 175, 175)';
	offset = 5; //pixels
	var point = [center_x - screen_x/2, center_y + screen_y/4];

	ctx.moveTo(point[0], point[1]);
	ctx.beginPath();
	ctx.lineTo(point[0] + offset, point[1] + offset);
	ctx.lineTo(point[0] + 285 + offset, point[1] + 75 - offset);
	point[0] += 285; point[1] += 75;
	ctx.lineTo(point[0] + offset, center_y + screen_y/2 - offset);
	ctx.lineTo(center_x - screen_x/2 + offset, center_y + screen_y/2 - offset);
	ctx.closePath();

  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();
}
function drawSystemBackground(ctx, center_x, center_y, system_x, system_y){
	ctx.strokeStyle = 'rgb(255, 255, 255';
	ctx.strokeRect(center_x - system_x/2 - 1, center_y - system_y/2 - 51, system_x + 2,system_y + 2);
}
function draw_ui_background(ctx, center_x, center_y, screen_x, screen_y) {
	grey = 'rgb(100, 100, 100)';
	ctx.strokeStyle = 'rgb(66,170,244)';
	ctx.strokeRect(center_x - screen_x/2, center_y - screen_y/2, screen_x,screen_y);

	ctx.strokeStyle = 'rgb(255,255,255)';
	ctx.strokeRect(center_x - screen_x/2 - 2, center_y - screen_y/2 -2, screen_x + 4, screen_y + 4);

  	// begin left ui-holder
  	ctx.strokeStyle = grey;	
  	var point = [center_x - screen_x/2, center_y + screen_y/4.5];

  	ctx.beginPath();
  	ctx.moveTo(point[0], point[1]);

  	ctx.bezierCurveTo(point[0], point[1] + 10, point[0], point[1] + 20, point[0] + 25, point[1] + 25);
  	point[0] += 25; point[1] += 25;

  	ctx.lineTo(point[0] + 225, point[1] + 45);
  	point[0] += 225; point[1] += 45;

  	ctx.bezierCurveTo(point[0] + 25, point[1] + 5, point[0] + 50, point[1] + 10, point[0] + 50, point[1] + 35);
  	point[0] += 50; point[1] += 25;

  	ctx.lineTo(point[0], center_y + screen_y/2);
  	ctx.lineTo(center_x - screen_x/2, center_y + screen_y/2);
  	ctx.closePath();
	
  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();


  	// begin right ui-holder
  	point = [center_x + screen_x/2, center_y + screen_y/4.5];

  	ctx.beginPath();
  	ctx.moveTo(point[0], point[1]);

  	ctx.bezierCurveTo(point[0], point[1] + 10, point[0], point[1] + 20, point[0] - 25, point[1] + 25);
  	point[0] -= 25; point[1] += 25;

  	ctx.lineTo(point[0] - 225, point[1] + 45);
  	point[0] -= 225; point[1] += 45;

  	ctx.bezierCurveTo(point[0] - 25, point[1] + 5, point[0] - 50, point[1] + 10, point[0] - 50, point[1] + 35);
  	point[0] -= 50; point[1] += 25;

  	ctx.lineTo(point[0], center_y + screen_y/2);
  	ctx.lineTo(center_x + screen_x/2, center_y + screen_y/2);
  	ctx.closePath();
	
  	ctx.stroke();
  	ctx.fillStyle = 'rgb(175, 175, 175)';
  	ctx.fill();
}
function draw_map_butt(ctx, center_x, center_y, active) {
	var color = 'rgba(0,0,0,0)';
	if (active) {
		color = 'rgba(255,170,0,0.7)';
	} else {
		color = 'rgba(22,86,142,0.7)';
	}

	ctx.beginPath();
	ctx.moveTo(center_x - 210, center_y + 254);
	ctx.strokeStyle = 'black';
	ctx.fillStyle = color;
	ctx.arc(center_x - 250, center_y + 254, 40, 0, Math.PI*2);
	ctx.stroke();
	ctx.fill();
	ctx.closePath();
	ctx.strokeStyle = 'white';
	for (x = 2; x < 5; x++) {
		ctx.beginPath();
		ctx.arc(center_x - 250, center_y + 254, x*8, 0, Math.PI*2);
		ctx.closePath();
		ctx.stroke();
	}
	ctx.beginPath();
	ctx.fillStyle = 'white';
	ctx.arc(center_x - 250, center_y + 254, 10, 0, Math.PI*2);
	ctx.arc(center_x - 250 + 16, center_y + 254 - 18, 3, 0, Math.PI*2);
	ctx.fill();
	ctx.closePath();
	ctx.beginPath();
	ctx.arc(center_x - 250 - 30, center_y + 254 + 13, 5, 0, Math.PI*2);
	ctx.arc(center_x - 250, center_y + 254 + 16, 2, 0, Math.PI*2);
	ctx.fill();
	ctx.closePath();
}
function draw_engi_butt(ctx, center_x, center_y, active) {
	var img = new Image();
	img.onload = function() {
		ctx.drawImage(img, center_x - 350, center_y + 222, 40, 40);
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
	ctx.arc(center_x - 315, center_y + 280, 10, 0, Math.PI/2);
	ctx.lineTo(center_x - 345, center_y + 290);
	ctx.arc(center_x - 345, center_y + 280, 10, Math.PI/2, Math.PI);
	ctx.lineTo(center_x - 355, center_y + 215);
	ctx.arc(center_x - 345, center_y + 215, 10, Math.PI, Math.PI*3/2);
	ctx.lineTo(center_x - 315, center_y + 205);
	ctx.arc(center_x - 315, center_y + 215, 10, Math.PI*3/2, Math.PI*2);
	ctx.closePath();
	ctx.fill();
	ctx.stroke();
}
function unactivate_butts(ctx, center_x, center_y, screen_x, screen_y) {
	draw_behind_butts(ctx, center_x, center_y);
	draw_map_butt(ctx, center_x, center_y, false);
	draw_engi_butt(ctx, center_x, center_y, false);
}
function distance(x1, x2, y1, y2) {
	var xsqr = Math.abs((x1-x2)*(x1-x2));
	var ysqr = Math.abs((y1-y2)*(y1-y2));
	return Math.sqrt(xsqr + ysqr);
}
function onClick(event) {
	//canvas = document.getElementById('canvas');
	ctx = canvas.getContext('2d');
	center_x = canvas.width/2 - 5;
	center_y = canvas.height/2;
	screen_x = 1000;
	screen_y = 600;

	var x = event.clientX;
    var y = event.clientY;
    var coords = "X coords: " + x + ", Y coords: " + y;
    document.getElementById("demo").innerHTML = coords;

	var bleep = new Audio();
    bleep.src = "dustyroom_multimedia_positve_correct_complete_ping.mp3";

    if (!butts.map && distance(x,center_x - 240,y,center_y + 260)<40) {
    	butts.map = true;
    	butts.engi = false;
    	unactivate_butts(ctx, center_x, center_y, screen_x, screen_y);
    	draw_map_butt(ctx, center_x, center_y, true);
	    bleep.play();
    }
    else if (!butts.engi && 320<x && x<370 && 525<y && y<615) {
    	butts.engi = true;
    	butts.map = false;
    	unactivate_butts(ctx, center_x, center_y, screen_x, screen_y);
    	draw_engi_butt(ctx, center_x, center_y, true);
	    bleep.play();
    }
}



// MAIN FUNCTION
function main(){
	canvas = document.getElementById('canvas');
	ctx = canvas.getContext('2d');
	canvas.width = window.innerWidth - 20;
	canvas.height = window.innerHeight - 30;

	center_x = canvas.width/2 - 5;
	center_y = canvas.height/2;


	createUI(ctx, center_x, center_y);
	link2server();
}