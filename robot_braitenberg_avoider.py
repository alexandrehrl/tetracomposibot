import math
import random
from robot import *

class Robot_player(Robot):
    team_name = "WallFollower_90"

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a"):
        super().__init__(x_0, y_0, theta_0, name=name, team=self.team_name)
        # memory : 0 = normal, >0 = mode secours (recul)
        self.memory = 0 
        self.last_front = 1.0
        self.stuck_counter = 0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        # --- 1. DÉTECTION DE BLOCAGE (Anti-stagnation) ---
        if sensors[sensor_front] < 0.2 and abs(self.last_front - sensors[sensor_front]) < 0.0001:
            self.stuck_counter += 1
        else:
            self.stuck_counter = 0
        self.last_front = sensors[sensor_front]

        if self.stuck_counter > 10:
            self.memory = 25 # Manoeuvre de secours
            self.stuck_counter = 0

        # --- 2. SUBSOMPTION : ÉTATS PRIORITAIRES ---
        
        # PRIORITÉ 1 : Sortir d'un angle mort (Recul puis pivot)
        if self.memory > 0:
            self.memory -= 1
            if self.memory > 15:
                return -0.7, 0.0, False # Recul pur
            else:
                return 0.0, 1.0, False  # Pivot sec

        # PRIORITÉ 2 : VIRAGE À 90° (Mur droit devant)
        # Si le mur est très proche devant, on arrête d'avancer et on pivote à 90°
        if sensors[sensor_front] < 0.25:
            # On tourne à droite (-1.0) si on longe le mur gauche
            return 0.0, -1.0, False 

        # --- 3. COMPORTEMENT DE CROISIÈRE (Lignes droites) ---
        target_dist = 0.4
        
        # Ralentissement prédictif pour préparer le virage à 90°
        speed_factor = min(1.0, sensors[sensor_front_left] * 1.2, sensors[sensor_front_right] * 1.2)
        translation = 1.0 * speed_factor

        # Suivi de mur latéral (Braitenberg)
        error = sensors[sensor_left] - target_dist
        rotation = max(-0.5, min(0.5, error * 2.0))

        # Gestion des coins sortants (le mur s'arrête)
        if sensors[sensor_left] > 0.8:
            translation = 0.4
            rotation = 0.8 # On tourne à gauche pour retrouver le mur

        return translation, rotation, False