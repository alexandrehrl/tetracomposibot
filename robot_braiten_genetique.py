from robot import *
import math
import random

class Robot_player(Robot):
    team_name = "EliteScanner"
    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=5000, it_per_evaluation=500):
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
        self.it_per_evaluation = it_per_evaluation
        self.max_trials = evaluations
        self.iteration = 0
        self.trial = 0
        
        # --- MÉMOIRE AUTORISÉE ---
        # Un seul entier autorisé pour gérer l'état (déblocage ou compteur)
        self.memory = 0 
        
        # --- INITIALISATION DES POIDS ---
        # Pour commencer de zéro, on utilise des poids aléatoires.
        # Pour l'étape suivante (Arène 1, 2...), remplacez par le contenu de best_weights.txt
        self.param = [0.8292524132602732, 0.944735304608056, 0.9753996242794112, 1.0, 0.3395547973458073, 0.22511198544187183, -0.561397055404428, 0.6799598284439122]
        
        self.best_param = self.param.copy()
        self.best_score = -1.0

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        
        # --- 1. ARCHITECTURE GÉNÉTIQUE : ÉVALUATION ET MUTATION ---
        if self.iteration % self.it_per_evaluation == 0:
            if self.iteration > 0:
                # Calcul de la fitness : Vitesse réelle * Expansion * Fluidité
                v_eff = self.log_sum_of_translation / self.it_per_evaluation
                dist_exp = math.sqrt((self.x - self.x0)**2 + (self.y - self.y0)**2) / 100.0
                r_eff = abs(self.log_sum_of_rotation / self.it_per_evaluation)
                # Pénalise les robots qui tournent sur eux-mêmes
                penalty_spin = 1.0 - math.tanh(r_eff * 2.0)
                
                score_final = v_eff * (0.5 + dist_exp) * penalty_spin
                
                if score_final > self.best_score:
                    self.best_score = score_final
                    self.best_param = self.param.copy()
                    print(f"Trial {self.trial} | New Best: {self.best_score:.4f}")
                    # Sauvegarde automatique des poids
                    with open("best_weights.txt", "w") as f:
                        f.write(str(self.best_param))

                # Mutation : on repart du meilleur parent et on modifie un gène au hasard
                self.param = self.best_param.copy()
                idx = random.randint(0, 7)
                self.param[idx] += random.uniform(-0.3, 0.3)
                self.param[idx] = max(-1.0, min(1.0, self.param[idx]))
                self.trial += 1

            self.iteration += 1
            self.memory = 0 
            return 0, 0, True # Reset pour l'évaluation suivante

        # --- 2. ARCHITECTURE DE SUBSOMPTION : PRIORITÉ DÉBLOCAGE ---
        # Si le robot avance trop peu (vitesse réelle < 0.03) pendant l'arène 4
        steps_current = self.iteration % self.it_per_evaluation
        if steps_current > 60 and self.memory == 0:
            v_reelle = self.log_sum_of_translation / (steps_current + 1)
            if v_reelle < 0.03: 
                self.memory = 25 # Active le mode secours pour 25 pas

        # Si le mode déblocage est actif, il prend la priorité (Subsumption)
        if self.memory > 0:
            self.memory -= 1
            self.iteration += 1
            # Manœuvre : recul massif et rotation pour sortir du coin
            return -0.7, 0.9, False 

        # --- 3. COMPORTEMENT DE BRAITENBERG (MODE NORMAL) ---
        # Entrées : Biais(1), Avant-Gauche, Avant, Avant-Droit
        inputs = [1.0, sensors[1], sensors[0], sensors[7]]
        
        # Translation (indices 0-3) et Rotation (indices 4-7) via Perceptron
        translation = math.tanh(sum(inputs[i] * self.param[i] for i in range(4)))
        rotation = math.tanh(sum(inputs[i] * self.param[i+4] for i in range(4)))

        self.iteration += 1        
        return translation, rotation, False