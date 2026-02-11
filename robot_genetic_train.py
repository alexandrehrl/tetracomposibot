from robot import * 
import math
import random

nb_robots = 0

class Robot_player(Robot):
    """
    Algorithme génétique pour optimiser comportement Braitenberg
    Objectif : Maximiser la couverture de territoire (Paint Wars)
    """
    
    team_name = "Genetic_Optimizer"
    robot_id = -1
    iteration = 0
    
    # Paramètres génétiques
    param = [1.000, 0.932, 0.121, -0.006, -0.074, -0.532, -0.719, -0.676, 1.000, -0.283, 1.000, 0.652]
    bestParam = []
    bestScore = -float('inf')
    
    # Configuration
    it_per_evaluation = 400
    trial = 0
    max_trials = 500
    
    # Score sur 3 conditions initiales
    current_score_sum = 0
    eval_count = 0  # 0, 1, 2 pour les 3 évaluations
    
    # Conditions initiales fixes
    initial_conditions = []
    
    # Tracking de couverture (pas de contrainte mémoire ici !)
    visited_cells = set()
    cell_size = 5  # Taille cellule en pixels
    
    # Log
    log_file = None
    
    def __init__(self, x_0, y_0, theta_0, name="n/a", team="n/a", evaluations=0, it_per_evaluation=400):
        global nb_robots
        self.robot_id = nb_robots
        nb_robots += 1
        
        self.it_per_evaluation = it_per_evaluation
        self.max_trials = evaluations // 3  # 3 évaluations par génération
        
        # 3 conditions initiales FIXES (pour comparabilité)
        self.initial_conditions = [
            (x_0, y_0, theta_0),
            (x_0 - 8, y_0 + 8, theta_0 + 60),
            (x_0 + 8, y_0 - 8, theta_0 - 60)
        ]
        
        # Initialisation aléatoire des 12 paramètres entre -1 et 1
        self.param = [random.uniform(-1.0, 1.0) for _ in range(12)]
        self.bestParam = self.param.copy()
        
        # Ouvre fichier de log
        self.log_file = open("genetic_log.csv", "w")
        self.log_file.write("trial,eval,score,best_score,params\n")
        
        super().__init__(x_0, y_0, theta_0, name=name, team=team)
        
        print(f"🧬 OPTIMISATION GÉNÉTIQUE DÉMARRÉE")
        print(f"   Générations: {self.max_trials}")
        print(f"   Itérations/éval: {self.it_per_evaluation}")
        print(f"   Total itérations: {self.max_trials * 3 * self.it_per_evaluation}")
    
    def reset(self):
        """Reset avec condition initiale courante"""
        x, y, theta = self.initial_conditions[self.eval_count]
        self.x = self.x0 = x
        self.y = self.y0 = y
        self.theta = self.theta0 = theta
        self.log_sum_of_translation = 0
        self.log_sum_of_rotation = 0
        self.visited_cells.clear()
    
    def compute_score(self):
        """
        FONCTION DE SCORE INTELLIGENTE pour Paint Wars
        
        Composantes:
        1. COUVERTURE (70%) : Nombre de cellules visitées
        2. VITESSE (20%) : Distance parcourue (translation effective)
        3. EFFICACITÉ (10%) : Pénalité rotation excessive
        """
        
        # 1. COUVERTURE : Récompense principale
        num_cells = len(self.visited_cells)
        coverage_score = num_cells * 10.0
        
        # 2. VITESSE : Translation effective moyenne
        avg_translation = self.log_sum_of_translation / self.it_per_evaluation
        velocity_score = avg_translation * 100.0
        
        # 3. EFFICACITÉ : Pénalité rotation
        avg_rotation = abs(self.log_sum_of_rotation / self.it_per_evaluation)
        efficiency_score = max(0, avg_translation) * (1.0 - min(1.0, avg_rotation))
        efficiency_score *= 50.0
        
        # Score total
        total = coverage_score + velocity_score + efficiency_score
        
        return total
    
    def update_coverage(self):
        """Enregistre cellule visitée"""
        cell_x = int(self.x / self.cell_size)
        cell_y = int(self.y / self.cell_size)
        self.visited_cells.add((cell_x, cell_y))
    
    def mutate(self, parent):
        """
        Mutation : modifie 1 à 2 paramètres avec bruit gaussien
        Sigma adaptatif : diminue avec les générations
        """
        child = parent.copy()
        
        # Nombre de mutations
        num_mut = random.randint(1, 2)
        
        # Sigma adaptatif (exploration → exploitation)
        progress = self.trial / max(1, self.max_trials)
        sigma = 0.3 * (1.0 - progress * 0.7)  # Décroît de 0.3 à 0.09
        
        for _ in range(num_mut):
            idx = random.randint(0, len(child) - 1)
            child[idx] += random.gauss(0, sigma)
            # Clamp entre -1 et 1
            child[idx] = max(-1.0, min(1.0, child[idx]))
        
        return child
    
    def step(self, sensors, sensor_view=None, sensor_robot=None, sensor_team=None):
        """
        Algorithme génétique (μ=1, λ=1) avec 3 conditions initiales
        """
        
        # ========== FIN D'UNE ÉVALUATION ==========
        if self.iteration % self.it_per_evaluation == 0 and self.trial < self.max_trials:
            
            if self.iteration > 0:
                # Calcule score de l'évaluation
                score = self.compute_score()
                self.current_score_sum += score
                
                print(f"  Condition {self.eval_count + 1}/3 : Score = {score:.1f} "
                      f"(Cellules: {len(self.visited_cells)})")
                
                self.eval_count += 1
                
                # ========== FIN DES 3 ÉVALUATIONS ==========
                if self.eval_count >= 3:
                    # Score moyen
                    avg_score = self.current_score_sum / 3.0
                    
                    # (μ+λ) : Garde le meilleur
                    if avg_score > self.bestScore:
                        self.bestScore = avg_score
                        self.bestParam = self.param.copy()
                        print(f"\n🏆 Génération {self.trial}: RECORD = {self.bestScore:.2f}")
                        print(f"   Params: {[f'{p:.3f}' for p in self.bestParam]}")
                    
                    # Log CSV
                    params_str = ";".join([f"{p:.4f}" for p in self.param])
                    self.log_file.write(f"{self.trial},{self.eval_count},{avg_score:.4f},"
                                      f"{self.bestScore:.4f},{params_str}\n")
                    self.log_file.flush()
                    
                    # Génère enfant par mutation
                    self.param = self.mutate(self.bestParam)
                    
                    # Reset pour prochaine génération
                    self.current_score_sum = 0
                    self.eval_count = 0
                    self.trial += 1
                
                # Passe à condition suivante
                self.iteration += 1
                return 0, 0, True  # Reset demandé
        
        # ========== FIN OPTIMISATION ==========
        if self.trial >= self.max_trials:
            if self.eval_count == 0 and self.iteration % self.it_per_evaluation == 0:
                print(f"\n✅ OPTIMISATION TERMINÉE !")
                print(f"🏆 Meilleur score: {self.bestScore:.2f}")
                print(f"\n📋 PARAMÈTRES OPTIMAUX À COPIER :")
                print(f"param = {self.bestParam}")
                self.log_file.close()
            
            # Rejoue le meilleur en boucle
            self.param = self.bestParam
        
        # ========== COMPORTEMENT BRAITENBERG ==========
        
        # Track couverture
        self.update_coverage()
        
        # Agrégation capteurs
        avant = (sensors[0] + sensors[1] + sensors[7]) / 3.0
        cotes = (sensors[2] + sensors[6]) / 2.0
        asymetrie = sensors[6] - sensors[2]
        asymetrie_avant = sensors[7] - sensors[1]
        
        # TRANSLATION
        translation = 0.6 + 0.4 * math.tanh(
            self.param[0] + 
            self.param[1] * avant +
            self.param[2] * cotes +
            self.param[3] * sensors[4]  # rear
        )
        
        # ROTATION
        rotation = math.tanh(
            self.param[4] + 
            self.param[5] * asymetrie +
            self.param[6] * asymetrie_avant +
            self.param[7] * avant +
            self.param[8] * sensors[3] +  # rear-left
            self.param[9] * sensors[5]    # rear-right
        )
        
        # ANTI-BLOCAGE
        if avant < 0.15:
            rotation += self.param[10] * 2.0
            translation *= self.param[11] * 0.5
        
        # Limite rotation
        rotation = max(-1.0, min(1.0, rotation))
        
        self.iteration += 1
        return translation, rotation, False