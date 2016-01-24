'''
Created on 24 jan. 2016

@author: Dirc
'''

# Implementation of classic arcade game Pong

import simplegui
import random

# initialize globals - pos and vel encode vertical info for paddles
WIDTH = 600
HEIGHT = 400       
BALL_RADIUS = 10
PAD_WIDTH = 8
PAD_HEIGHT = 80
HALF_PAD_WIDTH = PAD_WIDTH / 2
HALF_PAD_HEIGHT = PAD_HEIGHT / 2
LEFT = False
RIGHT = True

SCORE_SIZE = 40
multiplier = 1.05

# initialize ball_pos and ball_vel for new bal in middle of table
# if direction is RIGHT, the ball's velocity is upper right, else upper left
def spawn_ball(direction):
    global ball_pos, ball_vel # these are vectors stored as lists
    global ball_acc, paddle_acc, pad_counter
    # Accelerations
    ball_acc = 2    
    paddle_acc = 4
    
    # Counters
    pad_counter = 0
    
    # Ball positions
    ball_pos = [WIDTH / 2, HEIGHT / 2]
    
    initial_ball_vel = 2
    
    x = initial_ball_vel * random.randrange(120, 240) / float(WIDTH)
    y = initial_ball_vel * random.randrange(60, 180) / float(HEIGHT)
    
    if direction == True:
        ball_vel = [ x, -y ]
    else:
        ball_vel = [ -x, -y ]
                

# define event handlers
def new_game():
    global paddle1_pos, paddle2_pos, paddle1_vel, paddle2_vel  # these are numbers
    global score1, score2  # these are ints
    global ball_acc, paddle_acc
    
    # Initial score
    score1 = 0
    score2 = 0
    
    spawn_ball(RIGHT)
    
    # Paddles 
    # [ highestpoint, lowestpoint ]
    paddle1_pos = [[HALF_PAD_WIDTH, HEIGHT/2 - HALF_PAD_HEIGHT], [HALF_PAD_WIDTH, HEIGHT/2 + HALF_PAD_HEIGHT]]
    paddle2_pos = [[WIDTH-1 - HALF_PAD_WIDTH, HEIGHT/2 - HALF_PAD_HEIGHT], [WIDTH-1 - HALF_PAD_WIDTH, HEIGHT/2 + HALF_PAD_HEIGHT]]
    
    # paddle velocity
    paddle1_vel = 0
    paddle2_vel = 0
      
    
def draw(canvas):
    global score1, score2, paddle1_pos, paddle2_pos, ball_pos, ball_vel
    global paddle1_vel, paddle2_vel, ball_acc, pad_counter, paddle_acc
 
        
    # draw mid line and gutters
    canvas.draw_line([WIDTH / 2, 0],[WIDTH / 2, HEIGHT], 1, "White")
    canvas.draw_line([PAD_WIDTH, 0],[PAD_WIDTH, HEIGHT], 1, "White")
    canvas.draw_line([WIDTH - PAD_WIDTH, 0],[WIDTH - PAD_WIDTH, HEIGHT], 1, "White")
        
    # update ball
    ball_pos[0] += ball_acc * ball_vel[0]
    ball_pos[1] += ball_acc * ball_vel[1]
    
    # Borders
    if ball_pos[1] <= BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]
    elif ball_pos[1] >= HEIGHT - 1 - BALL_RADIUS:
        ball_vel[1] = -ball_vel[1]    
    
    # Guter score or Pad colision.
    if ball_pos[0] <= BALL_RADIUS + PAD_WIDTH:
        # Pad collison
        if ball_pos[1] > paddle1_pos[0][1] and ball_pos[1] < paddle1_pos[1][1]:
            ball_vel[0] = -ball_vel[0]
            pad_counter += 1
            ball_acc = ball_acc * ( multiplier ** pad_counter )
        else:       
            # Score
            score2 += 1
            # New start, change direction
            spawn_ball(RIGHT)
    elif ball_pos[0] >= WIDTH - 1 - BALL_RADIUS - PAD_WIDTH:
        # Pad collison
        if ball_pos[1] > paddle2_pos[0][1] and ball_pos[1] < paddle2_pos[1][1]:
            ball_vel[0] = -ball_vel[0]
            pad_counter += 1
            ball_acc = ball_acc * ( multiplier ** pad_counter )
        else:
            # Score
            score1 += 1
            # New start, change direction
            spawn_ball(LEFT)
    
    # draw ball
    canvas.draw_circle(ball_pos, BALL_RADIUS, 2*BALL_RADIUS, "White")
    
    # update paddle's vertical position, keep paddle on the screen    
    paddle1_pos[0][1] += paddle1_vel
    paddle1_pos[1][1] += paddle1_vel
    
    if paddle1_pos[0][1] < 0:
        paddle1_pos[0][1] = 0
        paddle1_pos[1][1] = PAD_HEIGHT
    elif paddle1_pos[1][1] > HEIGHT - 1:
        paddle1_pos[0][1] = HEIGHT - PAD_HEIGHT
        paddle1_pos[1][1] = HEIGHT
      
     
    paddle2_pos[0][1] += paddle2_vel
    paddle2_pos[1][1] += paddle2_vel
    
    if paddle2_pos[0][1] < 0:
        paddle2_pos[0][1] = 0
        paddle2_pos[1][1] = PAD_HEIGHT
    elif paddle2_pos[1][1] >= HEIGHT - 1:
        paddle2_pos[0][1] = HEIGHT - PAD_HEIGHT
        paddle2_pos[1][1] = HEIGHT

    
    # draw paddles
    canvas.draw_line( paddle1_pos[0], paddle1_pos[1], PAD_WIDTH, "White")
    canvas.draw_line( paddle2_pos[0], paddle2_pos[1], PAD_WIDTH, "White")
    
    # determine whether paddle and ball collide 
    #See "Guter score"    
    
    # draw scores
    # sans-serif of monospace
    canvas.draw_text(str(score1), [WIDTH/2 - 1.5 * SCORE_SIZE, 1.5 * SCORE_SIZE], SCORE_SIZE, "White", "monospace")
    canvas.draw_text(str(score2), [WIDTH/2 + 1.0 * SCORE_SIZE, 1.5 * SCORE_SIZE], SCORE_SIZE, "White", "monospace")
    
    
def keydown(key):
    global paddle1_vel, paddle2_vel
    
    # left paddle: w,s
    if key == simplegui.KEY_MAP['w']:
        paddle1_vel += -paddle_acc
    elif key == simplegui.KEY_MAP['s']:
        paddle1_vel += paddle_acc
    # right paddle: up, down
    if key == simplegui.KEY_MAP['up']:
        paddle2_vel += -paddle_acc
    elif key == simplegui.KEY_MAP['down']:
        paddle2_vel += paddle_acc
        
        
def keyup(key):
    global paddle1_vel, paddle2_vel
    # reverse paddle_acc to key_down
    # left paddle: w,s
    if key == simplegui.KEY_MAP['w']:   
        paddle1_vel += paddle_acc
    elif key == simplegui.KEY_MAP['s']:
        paddle1_vel += -paddle_acc
    # right paddle: up, down
    if key == simplegui.KEY_MAP['up']:
        paddle2_vel += paddle_acc
    elif key == simplegui.KEY_MAP['down']:
        paddle2_vel += -paddle_acc    

def restart_handler():
    new_game()

        
# create frame
frame = simplegui.create_frame("Pong", WIDTH, HEIGHT)
frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown)
frame.set_keyup_handler(keyup)
frame.add_button("Restart", restart_handler, 200)

# start frame
new_game()
frame.start()
