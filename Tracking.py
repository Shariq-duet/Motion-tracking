# from ursina import *
# import cv2
# import mediapipe as mp

# app = Ursina()
# window.color = color.black
# camera.position = (0, 5, -20)
# ground = Entity(model='plane', scale=20, color=color.dark_gray)
# EditorCamera()

# # Helper to create joints and bones
# def create_joint(c=color.blue, s=0.5):
#     joint = Entity(model='sphere', color=c, scale=s)
#     bone = Entity(model='cube', color=color.white, scale=(0.3, 1, 0.3)) 
#     return joint, bone

# # --- BODY PARTS ---
# # Adding the Head (using landmark 0 - nose)
# head, _ = create_joint(color.white, s=2) 

# # Upper Body
# r_sh, torso = create_joint(); l_sh, _ = create_joint()
# r_el, r_b1 = create_joint(color.green); l_el, l_b1 = create_joint(color.green)
# r_wr, r_b2 = create_joint(color.red); l_wr, l_b2 = create_joint(color.red)

# # Lower Body
# r_hp, r_b3 = create_joint(color.yellow); l_hp, l_b3 = create_joint(color.yellow)
# r_kn, r_b4 = create_joint(color.orange); l_kn, l_b4 = create_joint(color.orange)
# r_ak, r_b5 = create_joint(color.cyan); l_ak, l_b5 = create_joint(color.cyan)

# # AI Setup
# mp_pose = mp.solutions.pose
# pose = mp_pose.Pose(model_complexity=1, smooth_landmarks=True) # Complexity 1 is better for 3D
# cap = cv2.VideoCapture("test.mp4") # Change to "video.mp4" for files

# # EMA Constant: 0.1 means 10% new data, 90% old data. 
# # Lower = smoother but laggier. Higher = faster but jitterier.
# EMA_ALPHA = 0.15 
# base_floor_y = None

# def align(bone, p1, p2):
#     bone.position = (p1.position + p2.position) / 2
#     bone.look_at(p2.position, axis='up')
#     bone.scale_y = distance(p1.position, p2.position)

# def update():
#     global base_floor_y
#     ret, frame = cap.read()
#     if not ret: return
    
#     # Flip for mirror effect and process
#     frame = cv2.flip(frame, 1)
#     res = pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    
#     if not res.pose_world_landmarks: return
#     lm = res.pose_world_landmarks.landmark

#     sens = 18 
    
#     # Landmark mapping including the Nose (0) for the Head
#     mapping = [
#         (0, head), (12, r_sh), (11, l_sh), (14, r_el), (13, l_el), 
#         (16, r_wr), (15, l_wr), (24, r_hp), (23, l_hp), 
#         (26, r_kn), (25, l_kn), (28, r_ak), (27, l_ak)
#     ]

#     # Calibration for the floor
#     current_lowest = max(lm[27].y, lm[28].y)
#     if base_floor_y is None: base_floor_y = current_lowest

#     for id, ent in mapping:
#         # SMART LOGIC 1: Visibility Check
#         # If the camera isn't sure where the limb is, don't update it (prevents teleporting)
#         if lm[id].visibility > 0.6:
            
#             # Calculate Target
#             y_val = (-lm[id].y + base_floor_y) * sens
#             target_pos = Vec3(lm[id].x * sens, y_val, -lm[id].z * sens)
            
#             # SMART LOGIC 2: Exponential Moving Average (EMA)
#             # Instead of snapping, we move a fraction of the distance
#             ent.position = lerp(ent.position, target_pos, EMA_ALPHA)

#     # Align bones
#     align(torso, r_sh, l_sh)
#     align(r_b1, r_sh, r_el); align(r_b2, r_el, r_wr)
#     align(l_b1, l_sh, l_el); align(l_b2, l_el, l_wr)
#     align(r_b3, r_sh, r_hp); align(l_b3, l_sh, l_hp)
#     align(r_b4, r_hp, r_kn); align(l_b4, l_hp, l_kn)
#     align(r_b5, r_kn, r_ak); align(l_b5, l_kn, l_ak)

#     cv2.imshow("Mocap Feed", frame)

# app.run()
from ursina import *
import cv2
import mediapipe as mp

class PoseTracker:
    def __init__(self):
        # Initialize MediaPipe
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(model_complexity=1, smooth_landmarks=True)
        # self.cap = cv2.VideoCapture("https://192.168.100.229:8080/video") # Or your video path
        self.cap = cv2.VideoCapture("test.mp4") # Or your video path
        # EMA and Calibration settings
        self.EMA_ALPHA = 0.15
        self.base_floor_y = None
        self.sens = 18

        # The 'Root' entity allows you to move the whole character at once
        self.root = Entity()

        # Create Joints (Attached to Root)
        self.head,_ = self.create_joint(color.white, s=0.8)
        self.r_sh, self.torso = self.create_joint(); self.l_sh, _ = self.create_joint()
        self.r_el, self.r_b1 = self.create_joint(color.green); self.l_el, self.l_b1 = self.create_joint(color.green)
        self.r_wr, self.r_b2 = self.create_joint(color.red); self.l_wr, self.l_b2 = self.create_joint(color.red)
        self.r_hp, self.r_b3 = self.create_joint(color.yellow); self.l_hp, self.l_b3 = self.create_joint(color.yellow)
        self.r_kn, self.r_b4 = self.create_joint(color.orange); self.l_kn, self.l_b4 = self.create_joint(color.orange)
        self.r_ak, self.r_b5 = self.create_joint(color.cyan); self.l_ak, self.l_b5 = self.create_joint(color.cyan)

    def create_joint(self, c=color.blue, s=0.5):
        joint = Entity(model='sphere', color=c, scale=s, parent=self.root)
        bone = Entity(model='cube', color=color.white, scale=(0.3, 1, 0.3), parent=self.root)
        return joint, bone

    def align(self, bone, p1, p2):
        bone.position = (p1.position + p2.position) / 2
        bone.look_at(p2, axis='up') # Look at the joint entity
        bone.scale_y = distance(p1.position, p2.position)

    def update_pose(self):
        ret, frame = self.cap.read()
        # --- NEW LOOPING LOGIC ---
        # If 'ret' is False, the video has reached the end.
        if not ret: 
            # Rewind the video back to frame position 0
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # Read the very first frame again to keep the loop moving
            ret, frame = self.cap.read()
            
            # If it STILL fails, the file might be missing or corrupted, so we safely exit
            if not ret: 
                return
        
        frame = cv2.flip(frame, 1)
        res = self.pose.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if not res.pose_world_landmarks: return
        lm = res.pose_world_landmarks.landmark

        # Calibration for floor
        current_lowest = max(lm[27].y, lm[28].y)
        if self.base_floor_y is None: self.base_floor_y = current_lowest

        mapping = [
        (0, self.head), (12, self.r_sh), (11, self.l_sh), (14, self.r_el), 
        (13, self.l_el), (16, self.r_wr), (15, self.l_wr), (24, self.r_hp), 
        (23, self.l_hp), (26, self.r_kn), (25, self.l_kn), (28, self.r_ak), (27, self.l_ak)
    ]

        for id, ent in mapping:
            if lm[id].visibility > 0.6:
                y_val = (-lm[id].y + self.base_floor_y) * self.sens
                target_pos = Vec3(lm[id].x * self.sens, y_val, -lm[id].z * self.sens)
                # Apply EMA
                ent.position = lerp(ent.position, target_pos, self.EMA_ALPHA)

        # Update Bone Alignments
        self.align(self.torso, self.r_sh, self.l_sh)
        self.align(self.r_b1, self.r_sh, self.r_el)
        self.align(self.r_b2, self.r_el, self.r_wr)
        self.align(self.l_b1, self.l_sh, self.l_el)
        self.align(self.l_b2, self.l_el, self.l_wr)
        self.align(self.r_b3, self.r_sh, self.r_hp)
        self.align(self.l_b3, self.l_sh, self.l_hp)
        self.align(self.r_b4, self.r_hp, self.r_kn)
        self.align(self.l_b4, self.l_hp, self.l_kn)
        self.align(self.r_b5, self.r_kn, self.r_ak)
        self.align(self.l_b5, self.l_kn, self.l_ak)

        cv2.imshow("Mocap Feed", frame)
