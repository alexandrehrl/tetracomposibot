from robot import * 
import math
import random

nb_robots = 0
debug = False

class Robot_player(Robot):

    team_name = "Optimizer"
    robot_id = -1
    iteration = 0

    param = []
    bestParam = []
    bestScore = -1.0
    it_per_evaluation = 400
    trial = 0
    max_trials = 500
    current_score = 0

    x_0 = 0
    y_0 = 0
    theta_0 = 0 

    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        self.x_0 = x_0
        self.y_0 = y_0
        self.theta_0 = theta_0
        self.it_per_evaluation = it_per_evaluation

        self.param = [random.randint(-1, 1) for i in range(8)]
        super().__init__(x_0, y_0, theta_0, name=name, team=team)

    def reset():
        super().reset()

    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        if self.iteration % self.it_per_evaluation == 0 and self.trial < self.max_trials:
            if self.iteration > 0:

                if self.iteration %3 == 0:
                    if self.current_score > self.bestScore :
                        self.bestScore = self.current_score
                        self.bestParam = self.param.copy()
                        print(self.bestParam)
                        print(f"Essai {self.trial} : Nouveau record ! Score = {self.bestScore:.4f}")
                        indice_hasard = random.randint(0,7)
                        valeur_presente = self.param[indice_hasard]
                        if valeur_presente == 1:
                            self.param[indice_hasard] = random.choice([-1,0])
                        elif valeur_presente == -1:
                            self.param[indice_hasard] = random.choice([1,0])
                        else:
                            self.param[indice_hasard] = random.choice([-1,1])
                        self.current_score = 0 #on reset score toutes les 3 itérations
                    #problème d'élimination d'aléatoire

                
                    
                else:
                    self.x_0 = random.choice([self.x_0, self.x_0 -2, self.x_0 + 2])
                    self.y_0 = random.choice([self.y_0, self.y_0 -2, self.y_0 + 2])
                    self.theta_0 = random.choice([self.theta_0, self.theta_0 -1, self.theta_0 + 1])
                #ON TOUCHE PAS A CA
                v_moyenne = self.log_sum_of_translation / self.it_per_evaluation
                r_moyenne = abs(self.log_sum_of_rotation / self.it_per_evaluation)
                self.current_score += max(0, v_moyenne) * (1.0 - math.sqrt(min(1.0, r_moyenne)))
                #dans tous les cas on ajoute le score à lui même, il sera reset tous les modulo 3
                ####
                self.trial += 1
                self.iteration += 1
                return 0, 0, True 

        if self.trial >= (self.max_trials - 1):

            print(f"Replay du meilleur (Score final: {self.bestScore:.4f})")
            self.param = self.bestParam

        translation = math.tanh(self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right])
        
        rotation = math.tanh(self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right])

        self.iteration += 1        
        return translation, rotation, False