from ursina import *
import cv2
import mediapipe as mp

app = Ursina()

# --- 3D STAGE SETUP ---
# Create a ground plane so we have a sense of floor
ground = Entity(model='plane', collider='box', scale=10, texture='white_cube', texture_scale=(10,10), color=color.gray)

# Make the spheres BIGGER so we can see them clearly
shoulder = Entity(model='sphere', color=color.blue, scale=0.5, position=(0,2,0))
hand = Entity(model='sphere', color=color.red, scale=0.5, parent=shoulder)

# Move the camera to a better starting position
camera.position = (0, 5, -15)
camera.look_at(shoulder)

# --- AI SETUP ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(model_complexity=0) # Use 0 for speed on lower specs
cap = cv2.VideoCapture()

# Add these variables ABOVE your update function
smooth_factor = 0.15  # Adjust this: 0.01 is super smooth/slow, 0.9 is shaky/fast
sensitivity = 15     # How far the arms reach

def update():
    ret, frame = cap.read()
    if ret:
        # Flip frame so it feels like a mirror
        frame = cv2.flip(frame, 1)
        results = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if results.pose_world_landmarks:
            s = results.pose_world_landmarks.landmark[12] # Right Shoulder
            h = results.pose_world_landmarks.landmark[16] # Right Hand
            
            # --- TARGET POSITIONS ---
            target_shoulder = Vec3(s.x * sensitivity, -s.y * sensitivity + 5, -s.z * sensitivity)
            
            # Hand position RELATIVE to shoulder
            target_hand = Vec3((h.x - s.x) * sensitivity, 
                               -(h.y - s.y) * sensitivity, 
                               -(h.z - s.z) * sensitivity)
            
            # --- SMOOTHING (LERP) ---
            # Instead of jumping, we glide
            shoulder.position = lerp(shoulder.position, target_shoulder, smooth_factor)
            hand.position = lerp(hand.position, target_hand, smooth_factor)

# Pressing 'Tab' will let you fly around the scene with WASD to get a better angle

EditorCamera()
app.run()