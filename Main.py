# from ursina import *
# from Tracking import PoseTracker
# from PhysicsBody import PhysicalRig
# EditorCamera()
# app = Ursina()
# application.target_fps = 60 # LOCK FPS TO STOP JITTER

# # Environment
# ground = Entity(model='plane', scale=100, texture='grass', collider='box')
# orange_box = Entity(model='cube', scale=(4, 8, 5), 
#     position=(3, 4,2
# ), color=color.orange, collider='box')
# box_vel = Vec3(0,0,0)

# # Initialize Tracker and our New Rig
# tracker = PoseTracker()
# rig = PhysicalRig(tracker)

# def update():
#     global box_vel
#     tracker.update_pose()
    
#     # Update the physical model and get the kick force
#     kick_force = rig.update_rig(time.dt, target_object=orange_box)
    
#     # Apply kick force to the box
#     if kick_force.length() > 0:
#         box_vel += kick_force

#     # Simple Box Physics
#     box_vel.y += -9.8 * time.dt
#     box_vel *= 0.95
#     orange_box.position += box_vel * time.dt
#     if orange_box.y < 1: orange_box.y = 1; box_vel.y = 0

# app.run()from ursina import *
from email.mime import application
import time
from tkinter.ttk import Button
from turtle import color, distance
from xml.dom.minidom import Entity

from ursina import *

from Tracking import PoseTracker

from PhysicsBody import PhysicalRig

EditorCamera()

app = Ursina()

application.target_fps = 60 # LOCK FPS TO STOP JITTER

# --- MAIN MENU UI ---
# A variable to track if the game is actively playing
game_is_running = False 

# A parent entity to hold all menu items so we can hide them all at once
menu_screen = Entity(parent=camera.ui)

# Dark semi-transparent background
menu_bg = Entity(parent=menu_screen, model='quad', color=color.black66, scale=(2, 1), z=1)

# Game Title
title = Text(parent=menu_screen, text="VIRTUAL KICK", scale=5, origin=(0, 0), y=0.2, color=color.azure)
subtitle = Text(parent=menu_screen, text="AI Seekho 2026 Presentation", scale=2, origin=(0, 0), y=0.05, color=color.white)

# The Start Function
def start_game():
    global game_is_running
    game_is_running = True
    menu_screen.enabled = False  # Hide the menu completely

# The Buttons
start_button = Button(parent=menu_screen, text='START GAME', color=color.green, scale=(0.3, 0.1), y=-0.15, on_click=start_game)
quit_button = Button(parent=menu_screen, text='QUIT', color=color.red, scale=(0.3, 0.1), y=-0.3, on_click=application.quit)


# --- CAMERA & ENVIRONMENT ---
# Lock the camera behind the player, looking slightly down towards the goal
camera.position = (0, 7, -12)
camera.look_at(Vec3(0, 0, 10))

Sky() # Automatically adds a beautiful sky background

# The Field
ground = Entity(model='plane', scale=(30, 1, 40), color=color.lime, texture='grass', collider='box')

# Invisible Boundary Walls (Keeps the ball from rolling away forever)
wall_back  = Entity(model='cube', scale=(30, 10, 1), position=(0, 5, 20), collider='box', visible=False)
wall_right = Entity(model='cube', scale=(1, 10, 40), position=(15, 5, 0), collider='box', visible=False)
wall_left  = Entity(model='cube', scale=(1, 10, 40), position=(-15, 5, 0), collider='box', visible=False)

# The Ball (with a Trail!)
from ursina.prefabs.trail_renderer import TrailRenderer
ball = Entity(model='sphere', scale=1.5, position=(0, 2, 5), color=color.white, collider='sphere')
# Adds a cool fading tail to the ball when it moves fast
trail = TrailRenderer(parent=ball, thickness=10, color=color.orange, length=10)
ball_vel = Vec3(0,0,0)



# Initialize Tracker and our New Rig

tracker = PoseTracker()
rig = PhysicalRig(tracker)

# --- UI & EFFECTS ---
score = 0
score_ui = Text(text=f'SCORE: {score}', position=(-0.85, 0.45), scale=2, color=color.white, font='VeraMono.ttf')
goal_alert = Text(text='GOAL!', position=(0, 0), scale=5, color=color.yellow, origin=(0,0), enabled=False)

# A sphere that will flash and expand when you kick
impact_flash = Entity(model='sphere', color=color.azure, scale=0.1, unlit=True, visible=False)

def trigger_kick_effect(contact_position):
    impact_flash.position = contact_position
    impact_flash.visible = True
    impact_flash.scale = 0.5
    impact_flash.color = color.azure
    # Instantly expand and fade out to create a "shockwave" look
    impact_flash.animate_scale(3, duration=0.2, curve=curve.out_expo)
    impact_flash.animate_color(color.clear, duration=0.2)

# Goal Logic
goal_trigger = Entity(model='cube', scale=(8, 5, 1), position=(0, 2.5, 18), alpha=0.3, color=color.red, collider='box')

def score_goal():
    global score, ball_vel
    score += 1
    score_ui.text = f'SCORE: {score}'
    
    # Show "GOAL!" text, then hide it after 1.5 seconds
    goal_alert.enabled = True
    invoke(setattr, goal_alert, 'enabled', False, delay=1.5)
    
    # Reset ball
    ball.position = Vec3(0, 2, 5)
    ball_vel = Vec3(0,0,0)

def update():
    global ball_vel, game_is_running
    
    # --- GAME STATE CHECK ---
    # If the menu is still open, do not run any physics or tracking!
    if not game_is_running:
        return 
    # ------------------------

    tracker.update_pose()
    
    # Update the physical model and get the kick force
    kick_force = rig.update_rig(time.dt, target_object=ball)
    
    # Apply kick force and trigger visual effect
    if kick_force.length() > 0:
        ball_vel += kick_force
        # Only trigger the big flash if it's a strong kick
        if kick_force.length() > 2: 
            trigger_kick_effect(ball.world_position)

    # Box/Ball Physics
    ball_vel.y += -9.8 * time.dt
    ball_vel *= 0.96 # Air resistance
    ball.position += ball_vel * time.dt
    
    # Floor bounce
    if ball.y < 0.75: 
        ball.y = 0.75
        ball_vel.y *= -0.5

    # Check for Goal
    if distance(ball, goal_trigger) < 2.5:
        score_goal()

# Simple Goal Post (Two pillars and a crossbar)
goal_parent = Entity(position=(0, 0, 15)) # Move it back away from player
left_post = Entity(parent=goal_parent, model='cube', scale=(0.2, 5, 0.2), x=-4, y=2.5, color=color.white)
right_post = Entity(parent=goal_parent, model='cube', scale=(0.2, 5, 0.2), x=4, y=2.5, color=color.white)
crossbar = Entity(parent=goal_parent, model='cube', scale=(8, 0.2, 0.2), y=5, color=color.white)

# Hidden Trigger for Scoring
goal_trigger = Entity(parent=goal_parent, model='cube', scale=(8, 5, 1), y=2.5, alpha=0.1, color=color.green, visible=False)

def check_goal():
    # Simple distance check for the presentation
    if distance(ball, goal_trigger) < 2:
        print("GOAL!!!")
        ball.position = Vec3(0, 2, 5) # Reset ball position
        global ball_vel
        ball_vel = Vec3(0,0,0)

# --- UI SYSTEM ---
# Create a button in the top-left corner
reset_button = Button(
    text='Reset Ball', 
    color=color.azure, 
    scale=(0.2, 0.05), 
    position=(-0.7, 0.45) 
)

# The function that runs when the button is clicked
def reset_ball_position():
    ball.position = (0, 2, 5) # Your default starting position
    global ball_vel
    ball_vel = Vec3(0, 0, 0)  # Kill all momentum

# Link the button to the function
reset_button.on_click = reset_ball_position
# --- MOUSE PLACEMENT SYSTEM ---
# Ursina automatically calls this function whenever a key or mouse button is pressed
# --- MOUSE PLACEMENT SYSTEM ---
# Ursina automatically calls this function whenever a key or mouse button is pressed
def input(key):
    
    # Left click to teleport the ball
    if key == 'left mouse down':
        # We ensure the mouse is actually pointing at the ground
        if mouse.hovered_entity == ground:
            # We add a slight Y-axis offset so the ball drops from the air
            ball.position = mouse.world_point + Vec3(0, 1.5, 0)
            
            # Reset velocity so the ball drops straight down without inherited momentum
            global ball_vel
            ball_vel = Vec3(0, 0, 0)

    # Right click to teleport the player
    if key == 'E':
        # We perform the same check to ensure we are clicking the playable area
        if mouse.hovered_entity == ground:
            # We move the parent container of the PoseTracker.
            # All child joints, bones, and the dependent physics rig will follow instantly.
            tracker.root.position = mouse.world_point
app.run()