// CanvasDisplay constructor
function CanvasDisplay(parent, level) {
	this.canvas = document.createElement("canvas");
	this.canvas.width = level.length;
	this.canvas.height = level.height;
	parent.appendChild(this.canvas);
	this.cx = this.canvas.getContext("2d");
	
	this.animationTime = 0;
	
	this.isPaused = false;
	this.splashScreen = false;
	this.level = level;
	
	this.colors = {	text: 'rgb(240,240,240)', // almost white
					background: 'rgb(20,20,20)', // almost black
					actors: 'rgb(240,240,240)'} // almost white
					
	
} 
// Begin CanvasDisplay methods
CanvasDisplay.prototype.drawFrame = function(step) {
	// step will be the elapsed time since last frame
	this.animationTime += step; // total elapsed time;
	
	// entire display redraw after each frame
	this.clearDisplay();
	this.drawBackground();
	// both ship and asteroids are actors
	this.drawActors(); 
	// splashScreen is the initial pre-game screen with control instructions
	if (this.splashScreen)
		this.drawSplashScreen();
	if (this.level.status != 0 || this.isPaused)
		this.drawResolution(); 	// if level.status not 0 (normal running state),
								// will render some "won" or "lost" overlay
	this.drawPoints(); // draws playerPoints to top right
	this.drawLives();
	this.drawCurrentStage() // writes current stage playerPoints
};
CanvasDisplay.prototype.drawLives = function() {
	var shipSize = {width: 15, height: 20};
	var xMargin = 10;
	var yMargin = 10;
	for (var i = 0; i < this.level.livesLeft; i++) {
		var xOffset = 20 * i;
		
		// each ship is drawn facing north
		
		this.cx.beginPath();
		// top
		this.cx.moveTo(xMargin + shipSize.width/2 + xOffset, yMargin);
		// bottom left corner
		this.cx.lineTo(xMargin + xOffset, yMargin + shipSize.height);
		// bottom right corner
		this.cx.lineTo(xMargin + xOffset + shipSize.width, yMargin + shipSize.height);
		this.cx.closePath();
		this.cx.stroke();
	} 
}
CanvasDisplay.prototype.clearDisplay = function() {
	this.cx.clearRect(0, 0, 
					this.canvas.width, this.canvas.height);
};
CanvasDisplay.prototype.drawBackground = function() {
	this.cx.fillStyle = this.colors.background;
	this.cx.fillRect(0, 0, this.canvas.width, this.canvas.height);
};
CanvasDisplay.prototype.drawPoints = function() {
	this.cx.fillStyle = this.colors.text;
	this.cx.textAlign = "right";
	this.cx.textBaseline = "top";
	this.cx.font = "small-caps 100 48px sans-serif";
	
	this.cx.fillText(this.level.playerPoints, 
		this.canvas.width - 15, 0);
};
CanvasDisplay.prototype.drawCurrentStage = function() {
	var stageText;
	if (this.level.status == 0)
		stageText = 'stage: ' + this.level.currentStageCounter;
	else if (this.level.status == 1)
		stageText = 'winner winner chicken dinner';
	else
		stageText = 'damn';
	
	this.cx.fillStyle = this.colors.text;
	this.cx.textAlign = "right";
	this.cx.textBaseLine = "top";
	this.cx.font = "small-caps 100 20px sans-serif";
	
	// draw stageText underneath player points
	this.cx.fillText(stageText, this.canvas.width - 15, 48);
};
CanvasDisplay.prototype.drawActors = function() {
	for (var i = 0; i < this.level.actors.length; i++) {
		
		this.cx.strokeStyle = this.colors.actors;
		
		var actor = this.level.actors[i];
		// x and y of actor pos, offset by level origin and abbreviated
		var aX = this.level.origin.x + actor.pos.x;
		var aY = this.level.origin.y + actor.pos.y;
		
		// draw actor hitRadius (this is only for development)
		if (gameOptions.showHitRadius) {
		
			// drawn relative to actor position
		
			this.cx.beginPath();
			this.cx.arc(aX, aY, actor.hitRadius, 0, 7);
			this.cx.closePath();
			this.cx.stroke();
		}
		
		if (actor.type == "missile") {
		
			// drawn relative to actor position
		
			this.cx.beginPath();
			this.cx.moveTo(aX, aY);
			this.cx.lineTo(aX - Math.cos(actor.orient) * actor.size.y,
							aY - Math.sin(actor.orient) * actor.size.y);
			this.cx.closePath();
			this.cx.stroke();
		}
				
		if (actor.type == "player") {
		
			// drawn relative to actor position using translate and rotate
		
			this.cx.save(); 
			this.cx.translate(aX, aY); //offset to actor location
			this.cx.rotate(actor.orient + 0.5*Math.PI);
			
			this.cx.beginPath();
			// actor.size divided by 2 to draw actor "centered" on actor.pos
			this.cx.moveTo(0,-actor.size.y/2);
			this.cx.lineTo(-actor.size.x/2, actor.size.y/2);
			this.cx.lineTo(actor.size.x/2, actor.size.y/2);
			this.cx.closePath();
			this.cx.stroke();
			
			this.cx.restore();	
		}
		
		if (actor.type == "asteroid") {
		
			// NOT drawn relative to actor position. I wanted to try doing this
			// in absolute positioning because sometimes I want things to take 
			// far more time. 
			
			// Asteroids are rectangles. A rectangle has four corners. The
			// position of those corners can be found with triangles. 
			// The distance from the center of the rectangle to any corner is
			// the hypotenuse of a right triangle with vertices origin and
			// corner. 
			// So, dist to corner = sqrt( (height/2)^2 + (width/2)^2 ).
			// The angle of that right triangle, from the horizontal is
			// atan( (h/2)/(w/2) ). We'll call it ø.
			// 
			// Because the sum of all angles in a square (and rectangle) is 
			// 360º, we can find the second angle (to
			// the top left corner) by 180 - ø. We can find the third angle (to
			// the bottom left corner by 180 + ø. The last corner (bottom right)
			// with 360 - ø.
			// 
			// Remember that these angles have been from the horizontal. Some
			// methods expect you to be starting from the vertical.
			
			var hyp = Math.hypot(actor.size.x/2, actor.size.y/2);
			
			// Define the start position so everything is shorter.
			// this.level.origin.x + actor.pos.x is pretty long.
			
			// corner angle
			var theta = Math.atan( (actor.size.y/2) / (actor.size.x/2) );
			
			this.cx.beginPath();
			// first corner
			this.cx.moveTo(aX + hyp * Math.cos(theta + actor.orient),
						aY + hyp * Math.sin(theta + actor.orient));
			// second corner
			this.cx.lineTo(aX + hyp * Math.cos(Math.PI - theta + actor.orient),
						aY + hyp * Math.sin(Math.PI - theta + actor.orient));
			// third corner
			this.cx.lineTo(aX + hyp * Math.cos(Math.PI + theta + actor.orient),
						aY + hyp * Math.sin(Math.PI + theta + actor.orient));
			// fourth corner
			this.cx.lineTo(aX + hyp * Math.cos(-theta + actor.orient),
						aY + hyp * Math.sin(-theta + actor.orient));
			// closePath draws line back to first location in path and completes
			// the path
			this.cx.closePath();
			this.cx.stroke();
		}
		
		if (actor.type == "alien") {
		
			// drawn relative to actor position using translate
		
			var width = actor.size.x;
			var height = actor.size.y;
			
			this.cx.save();
			this.cx.translate(aX, aY);
			
			//draw alien ship outer bevel
			this.cx.beginPath();
			this.cx.moveTo(-width/2, 0);
			this.cx.lineTo(width/2, 0);
			this.cx.closePath();
			this.cx.stroke();
			
			//draw alien ship top half
			this.cx.beginPath();
			this.cx.moveTo((-width/2) * 0.75, 0);
			this.cx.quadraticCurveTo(0, - height * 0.25, (width/2) * 0.75, 0);
			this.cx.closePath();
			this.cx.stroke();
			
			// draw alien ship bottom half
			this.cx.beginPath();
			this.cx.moveTo((-width/2) * 0.75, 0);
			this.cx.quadraticCurveTo(0, height * 0.25, // control
									(width/2) * 0.75, 0); // goal
			this.cx.closePath();
			this.cx.stroke();
			
			// draw alien ship hatch
			this.cx.beginPath();
			this.cx.moveTo(-0.125*width, - height * 0.125);
			this.cx.quadraticCurveTo(0, - height * 0.5, // control
									 0.125*width, - height * 0.125) // goal
			// move back to path begin position so closePath doesn't
			// draw horizontal line
			this.cx.moveTo(-0.125*width, - height * 0.125);
			this.cx.closePath();
			this.cx.stroke();
			
			this.cx.restore();
		}
	}; 
};
CanvasDisplay.prototype.drawResolution = function() {
	this.cx.globalAlpha = 0.6;
	this.cx.fillStyle = "black";
	this.cx.fillRect(0, 0, this.canvas.width, this.canvas.height);
	this.cx.globalAlpha = 1.0;
	
	this.cx.font = "small-caps 700 48px sans-serif"
	this.cx.textBaseline = "middle";
	this.cx.textAlign = "center";
	this.cx.fillStyle = this.colors.text;
	
	if (this.level.status == -1) {
		this.cx.fillText("darn. you died.",
						this.canvas.width/2, this.canvas.height/2);
	} else if (this.level.status == 1) {
		this.cx.fillText("you won fool, props.",
						this.canvas.width/2, this.canvas.height/2);
	} else if (this.isPaused) {
		this.cx.fillText("we're paused homie",
			this.canvas.width/2, this.canvas.height/2);
	}
};
CanvasDisplay.prototype.drawSplashScreen = function() {
	this.cx.globalAlpha = 0.6;
	this.cx.fillStyle = "black";
	this.cx.fillRect(0, 0, this.canvas.width, this.canvas.height);
	this.cx.globalAlpha = 1.0;
	
	var textSize = 16;
	var lineHeight = textSize * 1.2;
	this.cx.font = "small-caps 700 " + textSize + "px sans-serif"
	this.cx.textBaseline = "middle";
	this.cx.textAlign = "center";
	this.cx.fillStyle = this.colors.text;
	
	this.cx.fillText("use LEFT and RIGHT keys to STEER",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 0);
	this.cx.fillText("use UP ARROW key to JET",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 1);		
	this.cx.fillText("use SPACEBAR key to SHOOT",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 2);		
	this.cx.fillText("use ESCAPE key to PAUSE",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 3);		
	this.cx.fillText("use F key to WARP (be careful!)",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 4);		
	this.cx.fillText("press B key to BEGIN",
		this.canvas.width/2, this.canvas.height/2 + lineHeight * 6);		

};

function Level(stages, player) {
	this.length = 600;
	this.height = 600;
	// game state default origin is in center of length and width
	this.origin = new Vector(this.length/2, this.height/2);
	// each actor present in actor is expected to have a position and size
	this.actors = [];
	this.playerPoints = 0;
	this.status = 0; // -1 is lost, 0 is running, 1 is won
	this.elapsedGameTime = 0;
	this.elapsedStageTime = 0;
	this.stages = stages;
	this.currentStageCounter = 1;
	this.parsedStage = this.parseStage(stages[this.currentStageCounter]);
	
	this.livesLeft = 3;
	this.playerRespawnAt = false; // always either true or future timeStamp
	
	this.player = player; // don't remove this; aliens need it for targeting
}

Level.prototype.checkClip = function(actor) {
	
	var clipType = false;
	
	/*
	- If there is hitRadius overlap between param actor and any actor in the 
	this.actors array OTHER than itself, return the other actor.
	- Finally, check if actor has hit an outer boundary of the level. If so, 
	return 'wall'.
	- If no collisions with anything detected, return clipType (which is default 
	set to false).
	*/
	
	for (var i = 0; i < this.actors.length; i++) {
		var other = this.actors[i];
		if (actor !== other) {
			// using these shorthand abbreviations to make things easier
			// to keep on fewer lines
			var ax = actor.pos.x, ay = actor.pos.y;
			var ox = other.pos.x, oy = other.pos.y;
			
			// if either actor or other doesn't have a hit radius, act like 
			// hitRadius is 0
			var ar, or; 
			if (actor.hitRadius) 
				ar = actor.hitRadius;
			else ar = 0;
			if (other.hitRadius)
				or = other.hitRadius;
			else or = 0;
				
			/*
			The hitRadius overlap pattern is this:
				
				If actor and other were in only one dimension (x axis), would
				their hit radii overlap? 
					- If no, then they do not overlap.
					- If yes, check to see if they would
					also overlap in the y dimension.
			*/
							
			// check right side (actorX > otherX)
			if (ax > ox && ax - ar < ox + or) {
					// check below (py < ay)
				if ((ay < oy && ay + ar > oy - or) ||
					// check above (py > ay)
					(ay > oy && ay - ar < oy + or)) {
					clipType = other;
				}
			// check left side (actorX < otherX)
			} else if (ax < ox && ax + ar > ox - or) {
					// check below (py < ay)
				if ((ay < oy && ay + ar > oy - or) ||
					// check above (py > ay)
					(ay > oy && ay - ar < oy + or)) {
					clipType = other;
				}
			}
		}
	}
	
	/*
	Finally, check for wall collision. Because this happens at the end of the 
	loop, it can and will take priority over other collisions and checkClip will 
	return "wall" if an actor would collide with both a wall and another actor.
	
	Also, wall collisions don't have to check for hit radius. This reduces the 
	sense of "teleporting" that objects can generate when moving from once side 
	of the level to the other.
	*/
	
	if (Math.abs(actor.pos.x) > this.length/2 ||
		Math.abs(actor.pos.y) > this.height/2)
		clipType = "wall";
	return clipType;
};
Level.prototype.transport = function(actor, newPos) {
	actor.pos = newPos;
};
Level.prototype.calcPointVal = function(actor) {
	return Math.floor(Math.max(actor.size.x, actor.size.y) * 10);
};
Level.prototype.removeActor = function(actor) {
	var index = this.actors.indexOf(actor);
	if (index > -1) {
		this.actors.splice(index, 1);
		// splice instead of delete because splice causes arrays to reindex
		return true;
	}
	else {
		return false;
	}
};
Level.prototype.checkForEnemies = function(actorArray) {
	function test(element) {
		return element.type != "player";
	}
	return actorArray.some(test);
};

var maxStep = 0.05; // this sets the maximum possible leap in animation time

// step will be time since last animation frame
Level.prototype.animate = function(step, keys) {
	
	/*
	This loop checks if the player needs to respawn and if the player is READY 
	to respawn. If those conditions are met, create an instance of Player to use 
	as a dummy spawn. Set the hitRadius of the testSpawn Player instance to 5x 
	normal so that the spawn area will be relatively safer.
	*/ 
	if (this.playerRespawnAt && this.elapsedGameTime > this.playerRespawnAt) {
		
		var testSpawn = new Player(new Vector(0,0));
		testSpawn.hitRadius = testSpawn.hitRadius * 5;

		if (this.checkClip(testSpawn) == false) {
			var newPlayer = new Player(new Vector(0,0));
			this.player = newPlayer;
			this.actors.unshift(newPlayer);
			this.playerRespawnAt = false;
		}
	}
	// remember, step will never be more than maxStep which was set as a global 
	// var
	while (step > 0) {
		var thisStep = Math.min(maxStep, step);
		this.actors.forEach(function(actor) {
			// first run through actor's act method (usually just updates 
			// position/orientation/velocity of actor)
			actor.act(thisStep, this, keys);
			// next remove 'spent' missiles, and short circuit if so
			if (actor.type == "missile" && actor.distTravel > 400) {
				this.removeActor(actor);
				return;
			}
			// Then, resolve collisions with checkClip (which returns either 
			// false, "wall", or the collided actor object from this.actors
			this.resolveCollision(actor, this.checkClip(actor));
		}, this); // pass in this so the inside loop has access to level scope
		
		this.elapsedGameTime += thisStep;
		this.elapsedStageTime += thisStep;
		// by decrementing step this way, animation frame times are chopped
		step -= thisStep;
	}	
	
	/* 
	After all actors have moved around and resolved their collisions, figure
	out if anything needs to spawn.
	
	getEnemyQue returns an object that looks like this: 
		{ 	que: ["alien", "asteroid", "etc"], 
			updatedParsedStage: ["stageParse version of an enemy", "another 
								one"] }
	*/
	
	var {	que: spawnQue, 
			updatedParsedStage: updatedStage} = this.getEnemyQue(
										this.elapsedStageTime,
										this.parsedStage,
										!this.checkForEnemies(this.actors)
										);
	
	/*	Add enemies from spawnQue. 
		spawnStageEnemies takes strings like "asteroid" or "alien" and turns 
		them into real Asteroid or Alien objects. It returns an array of the 
		objects it has created.
	*/
	this.spawnStageEnemies(spawnQue)
			.forEach(function(enemy) {this.actors.push(enemy)}.bind(this));
	
	/*	Old parsed stage will have an individual actor's spawned property set to
		false. updatedStage is just a copy of parsedStage when the spawned 
		actors have had their spawned property set to true. So, update the 
		internal parsedStage.
	*/
	this.parsedStage = updatedStage;
	
	/*	Finally, animate will check to see if it needs to move to the next 
		stage. 
		
		If no new actors are in spawnQue, and checkForEnemies returns false, the 
		level has nothing else to spawn and the next stage can begin. Also, 
		reset the elapsedStageTime back to 0.
		
		If the next stage does not HAVE any enemies, then the next stage does 
		not exist and the player has completed the last stage. The game is over 
		and the player has won.
	*/
	
	if (spawnQue.length == 0 && !this.checkForEnemies(this.actors)) {
		this.currentStageCounter++;
		var nextStage = this.parseStage(this.stages[this.currentStageCounter]);
		this.parsedStage = nextStage;
		this.elapsedStageTime = 0;
		
		// if parseStage returns nothing (no enemies to display), for the 
		// nextStage, then you have won
		if (nextStage.length == 0) {
			this.status = 1;
		}
	}
};
Level.prototype.parseStage = function(stageObject) {
	/* 
	This method 'decompresses' a condensed stage to an to an array where each 
	element represents a different enemy that should be spawned for that stage. 
	
	I wanted a way to be able to write levels quickly. I wanted a way to spawn 
	in various quantities of enemies at various delays, and I did want to have 
	to write those details for each enemy. 
	
	expected format for stageObject parameter:
	
	{
		'enemyType': 		{	'qty': #,
								'nextEnemyTime': # in seconds},
		'nextEnemyType':	{	'qty': #,
								'nextEnemyTime': # in seconds},
		'etc': {...}
	}
	
	desired sample array format to return:
	
	parsedStage = 	[	{	'enemyType': 'alien',
							'spawnTime': 20,
							'spawned': false	}, 
						{	'enemyType': 'asteroid',
							' spawnTime = 20,
							'spawned': false	},
						{etc...}
				 	];
	
	*/
		
	var parsedStage = [];
	for (enemyType in stageObject) {
		var lastSpawn = 0;
		for (var i = 0; i < stageObject[enemyType].qty; i++) {
			var enemy = Object.create(null);
			enemy.enemyType = enemyType;
			enemy.spawnTime = stageObject[enemyType].nextEnemyTime + lastSpawn;
			lastSpawn += stageObject[enemyType].nextEnemyTime;
			enemy.spawned = false;
			
			parsedStage.push(enemy);
		}
	}
	return parsedStage;

}; 
Level.prototype.getEnemyQue = function(elapsedStageTime, parsedStage, forceSpawn = false) {
	var que = [];
	var updatedStage = parsedStage;
	
	// pumps enemies to que if elapsedStageTime is adequate
	// also updates updatedStage if something is pushed to que
	for (var i = 0; i < updatedStage.length; i++) {
		var enemy = updatedStage[i];
		if (elapsedStageTime > enemy.spawnTime &&
			!enemy.spawned) {
			que.push(enemy.enemyType);
			enemy.spawned = true;
		}
	}
	
	// forced enemy pushing (this pumps something into que even if
	// elapsedStageTime isn't adequate
	
	if (forceSpawn) {  
		
		updatedStage.sort(function(a, b) {return a.spawnTime - b.spawnTime})
		var nextEnemy = updatedStage.find(function(enemy) {
			return enemy.spawned == false;
		});
		// if something is found, add it to the spawnQue and update updatedStage
		if (nextEnemy) {
			que.push(nextEnemy.enemyType);
			// update the parsedStage to reflect that it has been spawned
			nextEnemy.spawned = true
		};
	}
	
	return {'que': que, 'updatedParsedStage': updatedStage};
};
Level.prototype.spawnStageEnemies = function(list) {
	var enemies = [];
	for (var i = 0; i < list.length; i++) {
		if (list[i] == 'asteroid') {
			enemies.push(this.getRandomAsteroid());
		} else if (list[i] == 'alien') {
			enemies.push(new Alien({'pos': new Vector(300, getRandom(-250,250)),
									'velocity': new Vector(200, 0)
									})
						);
		}
	}
	return enemies;
};
Level.prototype.resolvePlayerDeath = function(respawnDelay = 5) {
	if (this.livesLeft > 0) {
		this.livesLeft -= 1;
		
		// remove player from actors list
		var playerIndex = this.actors.findIndex(function(e) {return e.type == "player"});
		this.actors.splice(playerIndex, 1);
		// setup future respawn time
		this.playerRespawnAt = this.elapsedGameTime + respawnDelay;
	} else {
		this.status = -1;
	}
};
Level.prototype.resolveCollision = function(actor, collision) {
	// don't do anything if no collision, or, collision is "safe" and not "wall"
	if (!collision || 
		((actor.createdByType == collision.type) && collision != "wall")) {
		return false;
	}
	if (actor.type == "player" && collision.type == "asteroid") {
		this.resolvePlayerDeath(5); // does livesLeft check, takes future respawnDelay as arg
	}
	if (actor.type == "missile") {
		if (collision.type == "asteroid") {
			// getChildren returns array of children asteroids or false 
			// if asteroid is too small
			var children = collision.getChildren();
			if (children) {
				for (var i = 0; i < children.length; i++) {
					this.actors.push(children[i]);
				}
			}
			// if actor is missile, and originally from player, add points	
			if (actor.createdByType == "player") {
				this.playerPoints += this.calcPointVal(collision);
			}
		}
		if (collision.type == "player") {
			this.resolvePlayerDeath(5); // does livesLeft check, takes future respawnDelay as arg 
			// this will only happen if collisions aren't "safe"
		}
		this.removeActor(actor); // finally, remove the missile actor
		this.removeActor(collision); // finally, remove the collision actor
	}
	/* 	This is confusing. By using this I'm basically 'cheating' the physics 
		engine. Logic is this: 
			- if wall is tripped, capture how much the actor has gone past the 
			wall (overStep).
			- Then 'wrap' the actor around to the other side of the axis + a 
			little bump (overStep * modifier). 
	*/
	if (collision == "wall") {
		if (Math.abs(actor.pos.x) > this.length/2) {
			var overStep = actor.pos.x % (this.length/2);
			actor.pos.x *= - 1;
			actor.pos.x = actor.pos.x + overStep * 1.5;
		}
		if (Math.abs(actor.pos.y) > this.height/2) {
			var overStep = actor.pos.y % (this.height/2);
			actor.pos.y *= -1;
			actor.pos.y = actor.pos.y + overStep * 1.5;
		}
	}
};
Level.prototype.getRandomAsteroid = function() {

	/* 	This is agreeably stupid, but I needed random Asteroid generation, I
		wrote it early on, and it works.
	*/
	var properties = Object.create(null);
	
	var rand1 = getRandom(-1, 1);
	var rand2 = getRandom(-1, 1);
	
	if (rand1 > rand2)
		properties.pos = new Vector(300*rand1, 300);
	else
		properties.pos = new Vector(300, 300*rand1);
	
	properties.spin = 5 * rand1;
	properties.velocity = new Vector(10 + 50 * rand1, 10 + 50 * rand2);
	properties.size = new Vector(15 + Math.abs(200 * rand1), 
								20 + Math.abs(200 * rand2));
	
	return new Asteroid(properties);
};

function Asteroid(
	// set defaults using destructuring
	{	pos = new Vector(300, 300),
		size = new Vector(35, 35),
		spin = 5,
		velocity = new Vector(35, 35)
	} = {}) {
	
	this.pos = pos;
	this.size = size;
	this.hitRadius = (this.size.x / 2 + this.size.y / 2) / 2; // average
	this.spin = spin;
	this.velocity = velocity;
	this.orient = 0;
}
Asteroid.prototype.type = "asteroid";
Asteroid.prototype.act = function(step) {
	this.rotate(step); // applies spin to current orientation
	this.updatePosition(step); // applies velocity to current position
};
Asteroid.prototype.getChildren = function() {

	/*
	Asteroids fracture in this pattern (whole square is parent asteroid):
	
	 ------------------
	|         |        |
	|    B    |   C    |
	|         |        |
	|------------------|
	|                  |
	|         A        |
	|                  |
	 ------------------
	
	A = childA
	B = childB
	C = childC
	
	*/
	
	if (Math.min(this.size.x, this.size.y) > 15) {
		
		var childAsteroids = [];
		var parent = this; // makes it easier to reason about
		
		var childA = Object.create(null);
		var childB = Object.create(null);
		var childC = Object.create(null);
		
		childA.pos = new Vector(parent.pos.x, parent.pos.y - parent.size.y/4);
		childA.size = new Vector(parent.size.x, parent.size.y/2);
		
		childB.pos = new Vector(parent.pos.x - parent.size.x/4,
			parent.pos.y + parent.size.y/4);
		childB.size = new Vector(parent.size.x/2, parent.size.y/2);
		
		childC.pos = new Vector(parent.pos.x + parent.size.x/4,
			parent.pos.y + parent.size.y/4);
		childC.size = new Vector(parent.size.x/2, parent.size.y/2);

		childA.orient = parent.orient;
		childB.orient = parent.orient;
		childC.orient = parent.orient;

		// childA will escape towards -0.5*PI off parent orient
		// childB will escape towards 0.75*PI off parent orient
		// childC will escape towards 0.25*PI off parent orient
		
		// velocity magnitude children will escape at
		var escapeMag = 5;
		
		// smaller child asteroids A and B will escape with higher magnitudes
		
		childA.velocity = parent.velocity.plus(new Vector(
			Math.cos(childA.orient - 0.5*Math.PI) * escapeMag,
			Math.sin(childA.orient - 0.5*Math.PI) * escapeMag)
		);
		childB.velocity = parent.velocity.plus(new Vector(
			Math.cos(childB.orient + 0.75*Math.PI) * escapeMag * 2,
			Math.sin(childB.orient + 0.75*Math.PI) * escapeMag * 2)
		);
		childC.velocity = parent.velocity.plus(new Vector(
			Math.cos(childC.orient + 0.25*Math.PI) * escapeMag * 2,
			Math.sin(childC.orient + 0.25*Math.PI) * escapeMag * 2)
		);
		
		childA.spin = parent.spin * 0.1;
		childB.spin = parent.spin * 0.1;
		childC.spin = parent.spin * 0.1;
		
		childAsteroids.push(new Asteroid(childA));
		childAsteroids.push(new Asteroid(childB));
		childAsteroids.push(new Asteroid(childC));
		
		return childAsteroids;
	} else
		// if an asteroid is under a certain size, it won't split smaller
		return false;
};
Asteroid.prototype.updatePosition = function(step) {
	this.pos.x += this.velocity.x * step;
	this.pos.y += this.velocity.y * step;
};
Asteroid.prototype.rotate = function(step) {
	this.orient += this.spin * step;
};

function Player(pos) {
	this.pos = pos;
	this.size = new Vector(15, 20);
	this.hitRadius = Math.max(this.size.x, this.size.y) / 2;
	this.turnSpeed = (180 / 180) * Math.PI; //turnSpeed in degrees
	this.velocity = new Vector(0, 0); // direction ship is drifting in
	this.accel = gameOptions.playerAccel || 100; 
	this.orient = 0; //in radians; begin pointing north
	this.gunsReady = 100; //less than 100 means shoot method won't do anything
	this.warping = false; // gets set to true for split second F key is pressed
}
Player.prototype.type = "player";
Player.prototype.act = function(step, level, keys) {
	this.warping = false;
	if (keys.warp) {
		this.pos = new Vector(Math.floor(300 * getRandom(-1, 1)),
								Math.floor(300 * getRandom(-1, 1)))
		this.warping = true;
	}
	this.shoot(step, level, keys);
	this.turn(step, keys); // affects orientation
	this.jet(step, keys); // affects velocity
	this.updatePosition(); //applies new velocity to position
	this.gunsReady += step * 500; //guns 'charge' over time
};
Player.prototype.shoot = function(step, level, keys) {	
	if (keys.space && this.gunsReady >= 100) {
			level.actors.push(new Missile({
				'initialPos': this.pos,
				'orient': this.orient,
				'createdByType': this.type
				}));
		this.gunsReady = 0; //this forces a delay after firing 
	}
};
Player.prototype.turn = function(step, keys) {
	if (keys.left && !keys.right) {
		this.orient -= this.turnSpeed * step;
	} else if (!keys.left && keys.right) {
		this.orient += this.turnSpeed * step;
	}
};
Player.prototype.jet = function(step, keys) {
	if (keys.up) {
		var jetVelocity = new Vector(Math.cos(this.orient) * this.accel * step,
									Math.sin(this.orient) * this.accel * step);
		this.velocity = this.velocity.plus(jetVelocity);
	}
};
Player.prototype.updatePosition = function() {
	this.pos.x += this.velocity.x;
	this.pos.y += this.velocity.y;
};

function Alien({pos = new Vector(300,0),
				velocity = new Vector(200,0),
				gunsReady = 0} = {}) {
	this.pos = pos;
	this.size = new Vector(30, 30);
	this.hitRadius = Math.max(this.size.x, this.size.y) / 2;
	this.velocity = velocity; 	// I treat this as a constant for now, like a
								// scaler instead of something with i and j
								// components that mean something directionally.
	this.gunsReady = gunsReady; //less than 1000 means shoot method won't do anything
	this.cycle = 0; // aliens move in sin wave behavior
	this.orient = 0;
}

Alien.prototype.type = "alien";
Alien.prototype.act = function(step, level) {
	this.cycle += step;
	this.shoot(step, level);
	this.updatePosition(step);
	this.gunsReady += step * 500;
};
Alien.prototype.shoot = function(step, level) {
	if (this.gunsReady >= 1000) {
		//figure out what direction to shoot
		var run = level.player.pos.x - this.pos.x;
		var rise = level.player.pos.y - this.pos.y;
		var hyp = Math.hypot(run, rise); 

		var alienMissile = new Missile({
			'initialPos': this.pos,
			'orient': 0, 	//this needs to be something other than 0, but i 
							// can't figure out how to get it
			'velocity': new Vector((run/hyp) * 5, (rise/hyp) * 5),
			'createdByType': this.type
			});
		level.actors.push(alienMissile);
		
		this.gunsReady = 0;
	}
};
Alien.prototype.updatePosition = function(step) {
	// sin wave behavior, scrolls left to right
	
	this.pos.x += this.velocity.x * step;
	this.pos.y += Math.sin(this.cycle * 2 * Math.PI) * this.velocity.x * step; 
};

function Missile({	initialPos = new Vector(0,0),
					orient = 0,
					velocity = undefined,
					createdByType = undefined} = {}) {
	this.pos = initialPos; 
	//	CanvasDisplay draws missiles trailing BEHIND position, 
	// 	in the opposite direction of orient (missiles have their body 'tail' 
	//	behind their position.
	this.size = new Vector(5, 10); 	// doesn't really matter, as missiles have 
									// no hit radius 
	this.orient = orient;
	this.velocity = velocity || new Vector(	Math.cos(this.orient) * 5,
											Math.sin(this.orient) * 5);
	this.distTravel = 0; // level.animate removes missiles once distTravel > 400
	this.createdByType = createdByType;
}
Missile.prototype.type = "missile";
Missile.prototype.act = function(step) {
	this.updatePosition(); // also updates distTravel
};
Missile.prototype.updatePosition = function() {
	var oldPos = this.pos;
	this.pos = this.pos.plus(this.velocity);
	this.distTravel += Math.hypot(this.pos.x - oldPos.x, this.pos.y - oldPos.y);
}

// helper stuff
function Vector(x, y) {
	this.x = x;
	this.y = y;
}
Vector.prototype.plus = function(other) {
	return new Vector(this.x + other.x, this.y + other.y);
};
Vector.prototype.times = function(factor) {
	return new Vector(this.x * factor, this.y * factor);
};

// returns a floating point between min and max
function getRandom(min, max) {
	return Math.random() * (max - min) + min;
};

function runAnimation(frameFunc) {
	var lastTime = null;
	function frame(time) {
		var stop = false;
		if (lastTime != null) {
			// this will break frames into a max of 100 milliseconds
			var timeStep = Math.min(time - lastTime, 100) / 1000;
			stop = frameFunc(timeStep) === false;
		}
		lastTime = time;
		if (!stop)
			requestAnimationFrame(frame);
	}
	requestAnimationFrame(frame);
}

var arrowCodes = {37: "left", 38: "up", 39: "right", 32: "space", 70: "warp"};

function trackKeys(codes) {
	var pressed = Object.create(null);
	function handler(event) {
		var down = event.type == "keydown";
		event.preventDefault();
		pressed[codes[event.keyCode]] = down;
	}
	addEventListener("keydown", handler);
	addEventListener("keyup", handler);

	return pressed;
}

var arrows = trackKeys(arrowCodes);

// Various game options. Maybe in the future this will be editable from outside
//	the game code.
var gameOptions = Object.create(null);
gameOptions = {
	'showHitRadius': false,
	'playerAccel': 20
};

/* Okay, so this part is hard because it's fairly abstracted and uses recursion.
	- The escape key alters var running to yes/pausing/no.
	- Animation takes an amount of time (called step), and has Level and Display 
	do their thing with that amount of time.
		- In some cases (game is paused, level status != 0), animation can 
		return false.
	- runAnimation is a wrapper for window.requestAnimation. It takes a function 
		that expects an amount of time (...like animation). At the end of 
		runAnimation, it runs itself again. This is the recursion. It will run 
		itself over and over unless the argument function returns false.
*/

function runLevel(level, Display) {
	var display = new Display(document.body, level, gameOptions);
	var running = "yes";
	display.splashScreen = true;
	//pausing event function
	function handleKey(event) {
		if (event.keyCode == 27	) { // keyCode 27 is escape key
			if (running == "no") {
				running = "yes";
				display.isPaused = false;
				runAnimation(animation)
			} else if (running == "yes") {
				running = "pausing";
			} else if (running == "pausing") {
				running = "yes";
			}
		}
	}
	addEventListener("keydown", handleKey);
	
	/*	Splash screen event function will become de-registered when splash
		screen == false;
	*/
	function endSplashScreen(event) {
		if (event.keyCode == 66) { //keyCode 66 is b key
			display.splashScreen = false;
			runAnimation(animation);
		}
	}
	
	function animation(step) {
	
	/* 	Animation is designed to be run as a callback. Anytime it returns false, 
		it will not run again. Else, it loops endlessly, each time being passed
		a time delta from the last time it ran (usually ~.016 seconds, so ~16
		milliseconds).
	*/ 
	
		if (display.splashScreen) {
			display.drawFrame();
			addEventListener("keydown", endSplashScreen);
			return false;
		} else
			removeEventListener("keydown", endSplashScreen);
		
		if (running == "pausing") {
			running = "no";
			display.isPaused = true;
			display.drawFrame();
			return false;
		}
		
		level.animate(step, arrows);
		display.drawFrame(step);
		if (level.status !== 0) {
			return false;
		}
	}
	runAnimation(animation);
}

function runGame(Display, stages) {
	var player = new Player(new Vector(0,0));
	var level = new Level(stages, player);
	level.actors.push(player);

	runLevel(level, Display);
}

var GAME_STAGES = Object.create(null);
GAME_STAGES = {
	1: {'asteroid': {	'qty': 1,
						'nextEnemyTime': 5
					},
		'alien': 	{	'qty': 1,
						'nextEnemyTime': 10
					}
		},
	2: {'asteroid': {	'qty': 3,
						'nextEnemyTime': 5
					},
		'alien': 	{	'qty': 3,
						'nextEnemyTime': 10
					}
		},
	3: {'asteroid': {	'qty': 5,
						'nextEnemyTime': 5
					},
		'alien': 	{	'qty': 5,
						'nextEnemyTime': 10
					}
		}

}

// end helper stuff

runGame(CanvasDisplay, GAME_STAGES);