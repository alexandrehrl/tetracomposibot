import math
import random
from robot import *

class Robot_player(Robot):
    team_name = "WallFollower_Expert"

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        super().__init__(x_0, y_0, theta_0, name=name, team=self.team_name)
        # memory : 0 = normal, >0 = mode secours (recul)
        self.memory = 0 
        self.last_front_val = 1.0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # --- 1. DÉTECTION DE BLOCAGE ---
        # Si la distance devant est quasi-nulle et ne change pas, on est coincé
        if abs(self.last_front_val - sensors[sensor_front]) < 0.0001 and sensors[sensor_front] < 0.2:
            self.memory = 30 # On passe à 30 pas de recul pour bien sortir de l'impasse

        self.last_front_val = sensors[sensor_front]

        # --- 2. PRIORITÉ HAUTE : RÉCUPÉRATION (Subsomption) ---
        if self.memory > 0:
            self.memory -= 1
            # On recule en tournant très fort pour changer d'orientation
            return -0.8, 1.0, False 

        # --- 3. ÉVITEMENT D'URGENCE ---
        # Si un mur est trop proche devant, on pivote sans avancer
        if sensors[sensor_front] < 0.2:
            return 0.0, 1.0, False 

        # --- 4. COMPORTEMENT NORMAL : LONGE-MUR ---
        target_dist = 0.4
        
        # Ralentissement si obstacles proches sur les côtés
        speed_factor = min(1.0, sensors[sensor_front_left] * 1.5, sensors[sensor_front_right] * 1.5)
        translation = 0.9 * speed_factor

        # Suivi du mur gauche
        error = sensors[sensor_left] - target_dist
        rotation = error * 2.5 

        # Si le mur disparaît (coin sortant), on tourne fort à gauche
        if sensors[sensor_left] > 0.8:
            rotation = 0.8
            translation = 0.4 

        return translation, rotation, False