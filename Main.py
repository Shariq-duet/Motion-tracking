from ursina import *
from Tracking import PoseTracker # Ensure Tracking.py has the class we discussed

app = Ursina()

# --- 1. THE ARENA ---
# A large grassy field to test your real-world movement range
ground = Entity(model='plane', scale=100, texture='grass', collider='box')
sky = Sky()
EditorCamera() # Allows you to move the editor camera to see the whole scene

# --- 2. THE BALL ---
# We'll use a physics-based ball
ball = Entity(
    model='sphere', 
    color=color.white, 
    scale=1, 
    position=(0, 0.5, 10), 
    collider='sphere'
)

# --- 3. THE PLAYER ---
tracker = PoseTracker()

# We create a "Ghost Foot" for collision. 
# It follows your real right ankle but has a collider to hit the ball.
foot_collider = Entity(
    model='sphere', 
    scale=0.8, 
    color=color.red, 
    alpha=0.5, 
    collider='sphere'
)

def update():
    # Update the MediaPipe logic
    tracker.update_pose()
    
    # Sync the Ghost Foot to your Right Ankle
    # tracker.r_ak[0] is the sphere entity of the right ankle
    foot_collider.position = tracker.r_ak.world_position

    # --- REAL TIME INTERACTION ---
    # Simple check: if the foot hits the ball
    if distance(foot_collider, ball) < 1.0:
        # Calculate the direction of the kick
        direction = (ball.position - foot_collider.position).normalized()
        # Move the ball forward based on the kick
        ball.position += direction * 0.5
        # Add a little bounce
        ball.animate_y(1.5, duration=0.2, curve=curve.out_expo)
        ball.animate_y(0.5, duration=0.2, delay=0.2, curve=curve.in_expo)

app.run()