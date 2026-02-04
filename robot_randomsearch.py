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

                v_moyenne = self.log_sum_of_translation / self.it_per_evaluation
                r_moyenne = abs(self.log_sum_of_rotation / self.it_per_evaluation)
                

                current_score = max(0, v_moyenne) * (1.0 - math.sqrt(min(1.0, r_moyenne)))
                #pas optimal mais fonctionne
                if current_score > self.bestScore:
                    self.bestScore = current_score
                    self.bestParam = self.param.copy()
                    print(f"Essai {self.trial} : Nouveau record ! Score = {self.bestScore:.4f}")
                self.trial += 1
                self.param = [random.randint(-1, 1) for i in range(8)]
                self.iteration += 1
                return 0, 0, True 
        if self.trial >= self.max_trials :

            print(f"Replay du meilleur (Score final: {self.bestScore:.4f})")
            self.param = self.bestParam

        translation = math.tanh(self.param[0] + self.param[1] * sensors[sensor_front_left] + self.param[2] * sensors[sensor_front] + self.param[3] * sensors[sensor_front_right])
        
        rotation = math.tanh(self.param[4] + self.param[5] * sensors[sensor_front_left] + self.param[6] * sensors[sensor_front] + self.param[7] * sensors[sensor_front_right])

        self.iteration += 1        
        return translation, rotation, False