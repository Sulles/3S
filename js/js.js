function vec(x,y){
	this.x = x;
	this.y = y;
}
vec.prototype.add = function(vec2){
	return vec(this.x+vec2.x, this.y+vec2.y);
}

// GAME DISPLAY CODE INSPIRED BY JONATHAN DEMIRGIAN
GameDisplay = function(center_x, center_y){
	this.canvas = document.createElement("canvas");
	this.center_x = center_x;
	this.center_y = center_y;
	this.w = 450; 	// width
	this.h = 450;	// height
	this.x_offset = 0;
	this.y_offset = -50;
	this.cx = this.canvas.getContext("2d");
	var starChance = 0.01; 	// percentage in decimal form (i.e. 0.01 == 1% chance)
	this.stars = [];
	this.initBackground(starChance);
	this.colors = {	LIGHTGRAY: 	'rgb(175, 175, 175)',
					GRAY: 		'rgb(100, 100, 100)',
					DARKGRAY: 	'rgb( 50,  50,  50)',
					BLACK: 		'rgb(  0,   0,   0)',
					NAVYBLUE: 	'rgb( 60,  60, 100)',
					WHITE: 		'rgb(255, 255, 255)',
					WHITERED: 	'rgb(255, 230, 230)',
					RED: 		'rgb(255,   0,   0)',
					REDBROWN: 	'rgb( 89,   0,   0)',
					PALERED: 	'rgb(255,  75,  75)',
					GREEN: 		'rgb(  0, 255,   0)',
					BLUE: 		'rgb(  0,   0, 255)',
					PALEBLUE: 	'rgb( 75,  75, 255)',
					YELLOW: 	'rgb(255, 255,   0)',
					PALEYELLOW: 'rgb(255, 255, 175)',
					ORANGE: 	'rgb(255, 128,   0)',
					PHOBOSCLR: 	'rgb(222, 184, 135)',
					DEIMOSCLR: 	'rgb(255, 222, 173)',
					BROWN: 		'rgb(255, 240, 220)',
					DARKBROWN: 	'rgb( 75,  75, 255)',
					BGCOLOR: 	'rgb(  0,   0,   0)'}
}
GameDisplay.prototype.drawFrame = function(step, Focus) {
	// step will be the elapsed time since last frame
	this.animationTime += step; // total elapsed time;

	this.clearDisplay();
	this.drawBackground();
	//this.drawObjects(Focus);
	//this.drawPlayers(Focus);
}
GameDisplay.prototype.clearDisplay = function() {
	this.cx.fillStyle = this.colors.BGCOLOR;
	this.cx.fillRect(this.center_x - this.w/2, this.center_y - this.h/2 + this.y_offset, this.w, this.h);
}
GameDisplay.prototype.initBackground = function(starChance) {
	for (x = 0; x < this.w; x++){
		for (y = 0; x < this.h; y++){
			if (Math.random() > this.starChance) {
				this.stars.push(vec(x,y))
			}
		}
	}
}
GameDisplay.prototype.drawBackground = function() {
	this.cx.strokeStyle = this.colors.WHITE;
	for (star in this.stars){
		this.ctx.moveTo(star.x, star.y);
		this.ctx.stroke();
	}
}





// ========================================================






function Body(data){
	this.Name = data.Name;
	this.Position = data.Position;
	this.Velocity = data.Velocity;
	this.e = data.e;
	if (this.e.length > 1){ this.e_ = norm(data.e); }
	else { this.e_ = this.e; }
	this.e = data.e;
	this.isCircular = data.isCircular;
	this.a = data.a;
	this.b = data.b;
	this.A = data.A;
	this.dAdt = data.dAdt;
	this.theta = 0;
	this.Parent = data.Parent;
}
Body.prototype.update = function(dt){
	// DON'T UPDATE OR CHANGE POSITION OR VEL OF OBJECTS THAT HAVE NO ORBITAL MECHANICS, SERVER WILL HANDLE THOSE

/*  def updateFromEllipse(self, dt):
    old_r = np.linalg.norm(self.Position)
    dTheta = self.a*self.b*self.n*dt/(old_r*old_r)
    self.theta += dTheta
    if (self.theta > 2*math.pi):
        self.theta = self.theta % 2*math.pi
    r = (self.a*(1-self.e_*self.e_))/(1+self.e_*math.cos(self.theta))
    self.updatePosFromRTheta(r)
    self.updateVel(dt)
    self.updateAcc(dt) */

	// REGULAR, NON-CIRCULAR ORBITAL MECHS
	if(this.e != null){
		P = (this.A/this.dAdt);
		n = 2*Math.PI/P;
		old_r = this.Position;
		dTheta = this.a*this.b*this.n*dt/(old_r*old_r);
		this.theta += dTheta;
		if (this.theta > 2*Math.PI){ this.theta %= 2*Math.PI; }
		r = (this.a*(1-this.e_*this.e_))/(1+this.e_*math.cos(this.theta));
		console.log(r);
	}
}
Body.prototype.getPosition = function(){
	return this.Position;
}
