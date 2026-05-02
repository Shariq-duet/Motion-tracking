from turtle import color, distance
from xml.dom.minidom import Entity

from ursina import *
# --- THE PHYSICAL HUMAN MODEL ---
# We define the parts of our 'Reality' model
body_parts = {
    'torso': Entity(model='cube', scale=(1.5, 3.5, 0.8), color=color.blue, collider='box', rigid_body=True),
    'head':  Entity(model='sphere', scale=0.8, color=color.white, collider='sphere', rigid_body=True),
    'l_arm': Entity(model='cube', scale=(0.4, 2, 0.4), color=color.blue, collider='box', rigid_body=True),
    'r_arm': Entity(model='cube', scale=(0.4, 2, 0.4), color=color.blue, collider='box', rigid_body=True),
    'l_leg': Entity(model='cube', scale=(0.6, 3, 0.6), color=color.blue, collider='box', rigid_body=True),
    'r_leg': Entity(model='cube', scale=(0.6, 3, 0.6), color=color.blue, collider='box', rigid_body=True),
}



class PhysicalRig:
    def __init__(self, tracker):
        self.tracker = tracker
        self.parts = {}
        self.prev_positions = {}
        
        # Jitter Protection settings
        self.deadzone = 0.08  # Ignore movements smaller than this
        self.follow_speed = 12
        
        # Create the 'Human' Block-Model
        self.setup_rig()

    def setup_rig(self):
        # We define the parts of our 'Reality' model
        self.parts = {
            'torso': Entity(model='cube', scale=(1.5, 3.5, 0.8), color=color.blue, alpha=0.7, collider='box',visible=False),
            'l_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), color=color.blue, alpha=0.7, collider='box',visible=False),
            'r_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), color=color.blue, alpha=0.7, collider='box',visible=False)
        }
        for name in self.parts:
            self.prev_positions[name] = Vec3(0,0,0)

    def update_rig(self, dt, target_object=None):
        mapping = {
            'torso': (self.tracker.r_sh.world_position + self.tracker.l_sh.world_position + self.tracker.r_hp.world_position + self.tracker.l_hp.world_position) / 4,
            'l_leg': self.tracker.l_ak.world_position,
            'r_leg': self.tracker.r_ak.world_position,
        }

        final_impact = Vec3(0,0,0)
        # LPF_ALPHA: Lower means smoother but slower (0.1 to 0.3 is best)
        LPF_ALPHA = 0.15 

        for name, target_pos in mapping.items():
            part = self.parts[name]
            
            # 1. CALCULATE THE GAP
            diff = target_pos - part.position
            dist = diff.length()

            # 2. UPDATED DEADZONE (Higher for World Landmarks)
            if dist > 0.15:
                # 3. SMOOTHED MOVEMENT (The Jitter Killer)
                # Instead of moving by speed * dt, we lerp toward the target
                # This naturally slows down the 'shaking'
                part.position = lerp(part.position, target_pos, LPF_ALPHA)
                
                # 4. VELOCITY FOR PHYSICS
                # We still need the velocity to kick the box
                velocity = diff / dt if dt > 0 else Vec3(0,0,0)
                
                if target_object and distance(part, target_object) < 1.8:
                    final_impact = velocity * 0.25
                    # Reality Constraint
                    part.position -= diff.normalized() * 0.2
        
        return final_impact
# from turtle import color
# from xml.dom.minidom import Entity
# from direct.actor.Actor import Actor  # <--- Add this line


# # from ursina import *

# # class PhysicalRig:
# #     def __init__(self, tracker):
# #         self.tracker = tracker
# #         self.parts = {}
# #         self.prev_positions = {}
        
# #         # 1. LOAD AS AN ACTOR (This is the 'Rigged' version)
# #         self.visual_model = Actor("human_model.glb")
# #         self.visual_model.reparent_to(scene) # Required for Actors in Ursina
# #         self.visual_model.set_scale(1.0)
# #         self.visual_model.set_color(color.smoke)
        
# #         # 2. EXPOSE THE JOINTS
# #         # Replace these names with the ones you found in listJoints()
# #         self.l_arm_joint = self.visual_model.exposeJoint(None, 'modelRoot', 'LeftArm')
# #         self.r_arm_joint = self.visual_model.exposeJoint(None, 'modelRoot', 'RightArm')

# #                 # Inside your PhysicalRig __init__
# #         self.visual_model = Actor("human_model.glb")
# #         self.visual_model.reparent_to(scene) # Actors need to be parented to the scene manually
# #         print("--- List of Bones Found ---")
# #         self.visual_model.listJoints()
        
# #         self.setup_rig()
        

# #     def setup_rig(self):
# #         # YOUR ORIGINAL RIG
# #         # We set visible=False so you only see the high-quality model
# #         self.parts = {
# #             'torso': Entity(model='cube', scale=(1.5, 3.5, 0.8), color=color.blue, alpha=0.7, collider='box', visible=True),
# #             'l_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), color=color.blue, alpha=0.7, collider='box', visible=True),
# #             'r_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), color=color.blue, alpha=0.7, collider='box', visible=True)
# #         }
# #         for name in self.parts:
# #             self.prev_positions[name] = Vec3(0,0,0)

# #     def update_rig(self, dt, target_object=None):
# #         # YOUR EXACT MAPPING
# #         mapping = {
# #             'torso': (self.tracker.r_sh.world_position + self.tracker.l_sh.world_position + 
# #                       self.tracker.r_hp.world_position + self.tracker.l_hp.world_position) / 4,
# #             'l_leg': self.tracker.l_ak.world_position,
# #             'r_leg': self.tracker.r_ak.world_position,
# #         }

# #         final_impact = Vec3(0,0,0)
# #         LPF_ALPHA = 0.15 

# #         # MANNEQUIN FOLLOWS TORSO
# #         if 'torso' in mapping:
# #             self.mannequin.position = lerp(self.mannequin.position, mapping['torso'], LPF_ALPHA)
# #             # Faces forward relative to the camera
# #             self.mannequin.look_at(self.mannequin.position + Vec3(0,0,1))
# #         # 3. APPLY ROTATION TO ARMS
# #         if self.tracker.l_el:
# #             # Point the exposed joint at your actual elbow/wrist tracking data
# #             self.l_arm_joint.look_at(self.tracker.l_el.world_position)
# #         # YOUR EXACT INTERACTION LOGIC
# #         for name, target_pos in mapping.items():
# #             part = self.parts[name]
# #             diff = target_pos - part.position
# #             dist = diff.length()

# #             if dist > 0.15:
# #                 part.position = lerp(part.position, target_pos, LPF_ALPHA)
# #                 velocity = diff / dt if dt > 0 else Vec3(0,0,0)
                
# #                 # Check distance between the hidden blocks and the orange box
# #                 if target_object and (part.world_position - target_object.world_position).length() < 1.8:
# #                     final_impact = velocity * 0.25
# #                     part.position -= diff.normalized() * 0.2
        
# #         return final_impact
    


# from ursina import *
# from direct.actor.Actor import Actor

# class PhysicalRig:
#     def __init__(self, tracker):
#         self.tracker = tracker
#         self.parts = {}
#         self.LPF_ALPHA = 0.15 

#         try:
#             self.visual_model = Actor("human_model.glb")
#             self.visual_model.reparent_to(scene)
            
#             # 1. SCALE & COLOR
#             # Adjust this number until the mannequin matches your skeleton height
#             self.visual_model.set_scale(1) 
#             self.visual_model.set_color(color.red)  # Make it red for visibility

#             # 2. CONTROL ALL JOINTS (Using your exact Joint List names)
#             # Arms
#             self.l_arm = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:LeftArm_09')
#             self.l_forearm = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:LeftForeArm_010')
#             self.r_arm = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:RightArm_033')
#             self.r_forearm = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:RightForeArm_034')
            
#             # Legs (For the kicking interaction)
#             self.l_up_leg = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:LeftUpLeg_056')
#             self.l_leg = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:LeftLeg_00')
#             self.r_up_leg = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:RightUpLeg_060')
#             self.r_leg = self.visual_model.controlJoint(None, 'modelRoot', 'mixamorig:RightLeg_061')

#         except Exception as e:
#             print(f"Rigging Error: {e}")

#         self.setup_rig()

#     def setup_rig(self):
#         # Your invisible physics boxes remain the same for stability
#         self.parts = {
#             'torso': Entity(model='cube', scale=(1.5, 3.5, 0.8), visible=False, collider='box'),
#             'l_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), visible=False, collider='box'),
#             'r_leg': Entity(model='cube', scale=(0.7, 3.5, 0.7), visible=False, collider='box')
#         }

#     def update_rig(self, dt, target_object=None):
#         final_impact = Vec3(0, 0, 0)
#         if not self.visual_model: return final_impact

#         # 1. GROUND THE MODEL (Hips center)
#         if self.tracker.r_hp and self.tracker.l_hp:
#             hip_center = (self.tracker.r_hp.world_position + self.tracker.l_hp.world_position) / 2
#             self.visual_model.set_pos(hip_center + Vec3(0, -3.0, 0))

#         # 2. THE STRETCH-KILLER (Directional Rotation)
#         def point_bone_clean(bone, joint_start, joint_end):
#             if bone and joint_start and joint_end:
#                 # Calculate the direction vector from start (e.g. Shoulder) to end (e.g. Elbow)
#                 direction = joint_end.world_position - joint_start.world_position
                
#                 # We point the bone at a point just 1 unit away in that direction
#                 # This prevents the bone from 'stretching' to a far-away coordinate
#                 local_target = bone.get_pos(scene) + direction.normalized()
#                 bone.look_at(local_target)
                
#                 # Force reset scale to ensure no distortion
#                 bone.set_scale(1)

#         # 3. MAPPING THE LIMBS (Start Joint -> End Joint)
#         # Left Arm: Shoulder to Elbow, Forearm to Wrist
#         point_bone_clean(self.l_arm, self.tracker.l_sh, self.tracker.l_el)
#         point_bone_clean(self.l_forearm, self.tracker.l_el, self.tracker.l_wr)

#         # Right Arm: Shoulder to Elbow, Forearm to Wrist
#         point_bone_clean(self.r_arm, self.tracker.r_sh, self.tracker.r_el)
#         point_bone_clean(self.r_forearm, self.tracker.r_el, self.tracker.r_wr)

#         # Left Leg: Hip to Knee, Leg to Ankle
#         point_bone_clean(self.l_up_leg, self.tracker.l_hp, self.tracker.l_kn)
#         point_bone_clean(self.l_leg, self.tracker.l_kn, self.tracker.l_ak)

#         # Right Leg: Hip to Knee, Leg to Ankle
#         point_bone_clean(self.r_up_leg, self.tracker.r_hp, self.tracker.r_kn)
#         point_bone_clean(self.r_leg, self.tracker.r_kn, self.tracker.r_ak)
#         # 5. PHYSICS LOGIC (Interaction with Orange Box)
#         # We use the invisible blue boxes (self.parts) for physical collisions
#         for name, part in self.parts.items():
#             # Define target landmark positions for the hidden boxes
#             phys_mapping = {
#                 'torso': hip_center,
#                 'l_leg': self.tracker.l_ak.world_position,
#                 'r_leg': self.tracker.r_ak.world_position
#             }
            
#             if name in phys_mapping:
#                 target_landmark = phys_mapping[name]
#                 # Smooth the hidden box movement
#                 part.position = lerp(part.position, target_landmark, self.LPF_ALPHA)
                
#                 # Check for impact with the orange box
#                 if target_object and (part.world_position - target_object.world_position).length() < 1.8:
#                     velocity = (target_landmark - part.position) / dt if dt > 0 else Vec3(0,0,0)
#                     final_impact = velocity * 0.25
#                     # Reality Constraint (Push back the leg slightly on impact)
#                     part.position -= (target_landmark - part.position).normalized() * 0.2
        
#         # 6. RETURN FINAL FORCE (Indented once, at the very bottom)
#         return final_impact