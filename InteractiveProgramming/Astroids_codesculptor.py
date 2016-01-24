'''
Created on 24 jan. 2016

@author: Dirc
'''

# program template for Spaceship
import simplegui
import math
import random

### globals for user interface
WIDTH = 800
HEIGHT = 600
score = 0
start_lives = 3
time = 0.5
started = False


### Inital values
soundtrack_volume = 0.5
# Ship
ship_acc_factor = 0.1
ship_turn_velocity = 0.05
friction = .01
truster_volume = 0.5
# Missiles
missile_speed_multiplier = 6
missile_lifespan = 50
missile_volume = 0.5
# Rocks
initial_rock_vel = 7
max_rock_spin = 10
rock_limit = 12

# Fixed initial values
rock_count = 0
lives = start_lives
#max_rock_vel = initial_rock_vel

### Helper functions / classes
class ImageInfo:
    def __init__(self, center, size, radius = 0, lifespan = None, animated = False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim
    
# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5,5], [10, 10], 3, missile_lifespan)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
soundtrack.set_volume(soundtrack_volume)
missile_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(missile_volume)
ship_thrust_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
ship_thrust_sound.set_volume(truster_volume)
explosion_sound = simplegui.load_sound("http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

# Initialise New Game
# initialize ship sprites sets
def startgame():
    global started, my_ship, rock_count, lives, score
    started = True
    # Initialize variables
    my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
    rock_count = 0
    lives = start_lives
    score = 0
    # Sound
    soundtrack.play()

def gameover():
    global started, rock_group, missile_group
    started = False
    rock_group = set([])
    missile_group = set([])
    soundtrack.rewind()
    
# helper functions to handle transformations
def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]

def dist(p,q):
    return math.sqrt((p[0] - q[0]) ** 2+(p[1] - q[1]) ** 2)

# Helper functions sprite groups
def process_sprite_group(sprite_set, canvas):
    sprite_aged = set([])
    for sprite in sprite_set:
        # Check age
        if sprite.alive() == False:
            sprite_aged.add(sprite)
        else:
            sprite.draw(canvas)
            sprite.update()
    sprite_set.difference_update(sprite_aged)

def group_collide(group, other_object):
    global explosion_group
    collision = False
    group_remove = set([])
    for sprite in group:
        if sprite.collide(other_object):
            group_remove.add(sprite)
            collision = True
            # Explosion "of other object"
            expl_pos = other_object.get_position()
            a_explosion = Sprite(expl_pos, [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)
            explosion_group.add(a_explosion)
    # Update group
    group.difference_update(group_remove)
    return collision

def group_group_collide(group1, group2):
    # Due to group_collide: elements of group1 determines explosion position.
    group_remove = set([])
    for sprite in group1:
        # Check for collision
        if group_collide(group2, sprite):
            group_remove.add(sprite)
    # Update group
    group1.difference_update(group_remove)
    return len(group_remove)

    
### Object classes
# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        
    def draw(self,canvas):
        if self.thrust:
            canvas.draw_image(self.image, [self.image_center[0] + self.image_size[0],self.image_center[1]], 
                              self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, 
                          self.pos, self.image_size, self.angle)
        
    def update(self):
        # Thrust update
        if self.thrust == False:
            ship_thrust_sound.rewind()
        else:
            self.vel[0] += angle_to_vector(self.angle)[0] * ship_acc_factor
            self.vel[1] += angle_to_vector(self.angle)[1] * ship_acc_factor
            ship_thrust_sound.play()
        self.vel[0] *= (1-friction)
        self.vel[1] *= (1-friction)
        
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        # Turn update
        self.angle += self.angle_vel
    
    def turn(self, angle_vel):
        self.angle_vel = angle_vel
    
    def thruster(self, thrust_bool):
        self.thrust = thrust_bool

    def shoot(self):
        global missile_group
        # initialize
        pos = [0,0]
        vel = [0,0]
        # Position and movements
        pos[0] = self.pos[0] + angle_to_vector(self.angle)[0] * self.radius
        pos[1] = self.pos[1] + angle_to_vector(self.angle)[1] * self.radius
        vel[0] = self.vel[0] + angle_to_vector(self.angle)[0] * missile_speed_multiplier
        vel[1] = self.vel[1] + angle_to_vector(self.angle)[1] * missile_speed_multiplier
        # Modulo screen end
        pos[0] %= WIDTH
        pos[1] %= HEIGHT
        # Define missile        
        a_missile = Sprite(pos, vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)

    def get_position(self):
        return self.pos
        
    def get_radius(self):
        return self.radius
        
        
# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound = None):
        self.pos = [pos[0],pos[1]]
        self.vel = [vel[0],vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()
   
    def draw(self, canvas):
        # Check if animated
        if self.animated and self.age < self.lifespan:
            canvas.draw_image(self.image, 
                              [self.image_center[0] + (self.age * self.image_size[0]), self.image_center[1]],
                              self.image_size, self.pos, self.image_size, self.angle)
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, 
                          self.pos, self.image_size, self.angle)
    
    def update(self):
        self.angle += self.angle_vel
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        self.pos[0] %= WIDTH
        self.pos[1] %= HEIGHT
        # Update age
        self.age += 1
        
    def alive(self):
        if self.age >= self.lifespan:
            return False
        else:
            return True
        
    def get_position(self):
        return self.pos
        
    def get_radius(self):
        return self.radius
    
    def collide(self,other_object):
        r1 = self.radius
        r2 = other_object.get_radius()
        distance = dist(self.pos,other_object.get_position())
        if distance <= r1 + r2:
            return True
        else:
            return False
        
### Event handlers
# Key handlers
def keydown(key):
    global my_ship
    # Turn ship: left, right
    if key == simplegui.KEY_MAP['right']:
        my_ship.turn(ship_turn_velocity)
    elif key == simplegui.KEY_MAP['left']:
        my_ship.turn(-ship_turn_velocity)
    # Move ship: front
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thruster(True)
    # Shoot
    elif key == simplegui.KEY_MAP['space']:
        my_ship.shoot()

def keyup(key):
    global ship_angle_vel, my_ship
    # Turn ship: left, right
    if key == simplegui.KEY_MAP['right']:
        my_ship.turn(0)
    elif key == simplegui.KEY_MAP['left']:
        my_ship.turn(0)  
    # Move ship: front
    elif key == simplegui.KEY_MAP['up']:
        my_ship.thruster(False)

# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        # Start Game
        startgame()


# Draw handler        
def draw(canvas):
    global time, lives, score, started, max_rock_vel
    global rock_group, missile_group
    
    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2], [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # Draw and Update ship and sprites
    my_ship.draw(canvas)
    my_ship.update()
    process_sprite_group(rock_group,canvas)
    process_sprite_group(missile_group,canvas)
    process_sprite_group(explosion_group,canvas)
    #a_explosion.draw(canvas)
    #a_explosion.update()
    
    # Determine any collisions
    if group_collide(rock_group,my_ship):
        lives -= 1
    
    # Score: missile hits rock
    score += 10 * group_group_collide(rock_group, missile_group)

    # Increase difficulty by increasing rock velocity
    max_rock_vel = initial_rock_vel + score // 10
    
    # Draw life and score
    text_size = 25
    canvas.draw_text('Lives', (50, 50), text_size, 'White', 'serif')
    canvas.draw_text(str(lives), (50, 80), text_size, 'White', 'serif')
    canvas.draw_text('Score', (WIDTH - 100, 50), text_size, 'White', 'serif')
    canvas.draw_text(str(score), (WIDTH - 100, 80), text_size, 'White', 'serif')
  
    # Game Over
    if lives <= 0:
        gameover()  
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())
        
# timer handler that spawns a rock    
def rock_spawner():
    global rock_group, rock_count
    if len(rock_group) <= rock_limit and started:
        # initialize
        pos = [0,0]
        vel = [0,0]
        spin = 0
        # Generate randomness
        pos[0] = random.randrange(0,WIDTH)
        pos[1] = random.randrange(0,HEIGHT)
        vel[0] = random.randrange(-max_rock_vel,max_rock_vel) / 10.0
        vel[1] = random.randrange(-max_rock_vel,max_rock_vel) / 10.0
        spin = random.randrange(-max_rock_spin,max_rock_spin) / 1000.0
        # Modulo screen end
        pos[0] %= WIDTH
        pos[1] %= HEIGHT
        # Define rock
        a_rock = Sprite(pos, vel, 0, spin, asteroid_image, asteroid_info)
        # Create rock, unless to close to the ship
        if a_rock.collide(my_ship):
            pass
        else:
            rock_group.add(a_rock)
    
# initialize frame
frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship sprites sets
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
rock_group = set([])
missile_group = set([])
explosion_group = set([])
#a_explosion = Sprite([WIDTH / 3, HEIGHT / 3], [0,0], 0, 0, explosion_image, explosion_info, explosion_sound)


# register handlers
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.set_mouseclick_handler(click)
frame.set_draw_handler(draw)

timer = simplegui.create_timer(1000.0, rock_spawner)

# get things rolling
timer.start()
frame.start()
