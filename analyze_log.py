#!/usr/bin/env python3
"""
Analyseur automatique de logs out.txt
Lance ce script après avoir exécuté le jeu pour obtenir un résumé des problèmes
"""

import re
from collections import defaultdict

def analyze_log(filename="out.txt"):
    print("="*80)
    print("ANALYSEUR AUTOMATIQUE DE LOGS - PAINT WARS")
    print("="*80)
    
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Fichier {filename} introuvable!")
        print("Vérifie que le jeu a bien été lancé avec DEBUG_ENABLED = True")
        return
    
    # Statistiques globales
    total_steps = len(re.findall(r'\[Step \d+\]', content))
    total_robots = len(re.findall(r'>>> ROBOT \d+ INITIALIZED', content))
    
    print(f"\n📊 STATISTIQUES GLOBALES")
    print(f"   Total steps tracés: {total_steps}")
    print(f"   Nombre de robots: {total_robots}")
    
    # Analyse par robot
    for robot_id in range(total_robots):
        print(f"\n{'='*80}")
        print(f"🤖 ROBOT {robot_id}")
        print(f"{'='*80}")
        
        # Extraire les sections du robot
        robot_pattern = f'\[Step \d+\] ===== ROBOT {robot_id} =====(.*?)(?=\[Step \d+\]|$)'
        robot_steps = re.findall(robot_pattern, content, re.DOTALL)
        
        if not robot_steps:
            print(f"   ⚠️  Aucun log trouvé pour Robot {robot_id}")
            continue
        
        # Compteurs de comportements
        behaviors = defaultdict(int)
        for step in robot_steps:
            if "DEBLOCAGE" in step:
                behaviors["DÉBLOCAGE"] += 1
            elif "LABYRINTHE" in step:
                behaviors["LABYRINTHE"] += 1
            elif "EVIT_ROBOT" in step:
                behaviors["ÉVITEMENT_ROBOT"] += 1
            elif "CROISIERE" in step:
                behaviors["CROISIÈRE"] += 1
        
        print(f"\n   📈 Répartition des comportements:")
        total_behaviors = sum(behaviors.values())
        for behavior, count in sorted(behaviors.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_behaviors * 100) if total_behaviors > 0 else 0
            print(f"      {behavior:20s}: {count:4d} steps ({percentage:5.1f}%)")
        
        # Détection de problèmes
        print(f"\n   🔍 Détection de problèmes:")
        
        # 1. Memory élevée (blocage)
        high_memory = []
        for i, step in enumerate(robot_steps):
            memory_match = re.search(r'Memory final: (\d+)', step)
            if memory_match:
                memory = int(memory_match.group(1))
                if memory > 15:
                    high_memory.append((i, memory))
        
        if high_memory:
            print(f"      ⚠️  Memory > 15 détectée {len(high_memory)} fois")
            print(f"         Max memory: {max(m for _, m in high_memory)} (step {high_memory[-1][0]})")
            if len(high_memory) > 10:
                print(f"         ❌ BLOCAGES FRÉQUENTS ! Vérifie steps autour de {high_memory[0][0]}-{high_memory[-1][0]}")
        else:
            print(f"      ✅ Pas de blocage détecté (memory toujours < 15)")
        
        # 2. Oscillations (changements rotation rapides)
        oscillations = 0
        last_rotation = None
        for step in robot_steps:
            rotation_match = re.search(r'Rotation: (-?\d+\.\d+)', step)
            if rotation_match:
                rotation = float(rotation_match.group(1))
                if last_rotation is not None:
                    # Si rotation change de signe et magnitude > 0.5
                    if abs(rotation - last_rotation) > 1.0 and rotation * last_rotation < 0:
                        oscillations += 1
                last_rotation = rotation
        
        if oscillations > len(robot_steps) * 0.1:  # Plus de 10% des steps
            print(f"      ⚠️  Oscillations détectées : {oscillations} changements brusques")
            print(f"         ❌ ZIGZAG EXCESSIF ! Gain P-controller trop élevé")
        else:
            print(f"      ✅ Pas d'oscillations excessives ({oscillations} changements)")
        
        # 3. Vitesse moyenne
        translations = []
        for step in robot_steps:
            trans_match = re.search(r'Translation: (-?\d+\.\d+)', step)
            if trans_match:
                translations.append(float(trans_match.group(1)))
        
        if translations:
            avg_translation = sum(translations) / len(translations)
            print(f"      📊 Vitesse moyenne: {avg_translation:.3f}")
            if avg_translation < 0.6:
                print(f"         ⚠️  VITESSE FAIBLE ! Robot trop prudent ou bloqué souvent")
            elif avg_translation > 0.85:
                print(f"         ✅ Bonne vitesse moyenne")
        
        # 4. Taux de déblocage
        deblocage_rate = (behaviors["DÉBLOCAGE"] / total_behaviors * 100) if total_behaviors > 0 else 0
        if deblocage_rate > 15:
            print(f"      ❌ Taux de déblocage élevé ({deblocage_rate:.1f}%)")
            print(f"         Le robot passe trop de temps coincé !")
        elif deblocage_rate > 5:
            print(f"      ⚠️  Taux de déblocage modéré ({deblocage_rate:.1f}%)")
        else:
            print(f"      ✅ Taux de déblocage faible ({deblocage_rate:.1f}%)")
    
    # Recommandations globales
    print(f"\n{'='*80}")
    print(f"💡 RECOMMANDATIONS")
    print(f"{'='*80}")
    
    # Vérifie si fichier très long
    if total_steps > 10000:
        print(f"⚠️  Fichier très long ({total_steps} steps) = beaucoup d'itérations")
        print(f"   Conseil: Teste sur moins d'itérations pour debug rapide")
    
    # Cherche patterns globaux
    total_deblocage = sum(1 for line in content.split('\n') if 'DEBLOCAGE' in line)
    if total_deblocage > total_steps * 0.1:
        print(f"\n❌ PROBLÈME MAJEUR: Trop de déblocages globaux ({total_deblocage})")
        print(f"   → Seuils de détection trop sensibles")
        print(f"   → OU arène mal adaptée aux comportements")
    
    total_croisiere = sum(1 for line in content.split('\n') if 'CROISIERE' in line)
    croisiere_rate = (total_croisiere / total_steps * 100) if total_steps > 0 else 0
    if croisiere_rate > 70:
        print(f"\n⚠️  Beaucoup de croisière ({croisiere_rate:.1f}%)")
        print(f"   → Comportements spécialisés (labyrinthe) peu actifs")
        print(f"   → Vérifie seuils d'activation")
    
    print(f"\n{'='*80}")
    print(f"Pour analyse détaillée, cherche dans out.txt :")
    print(f"   - 'Memory final: [2-9][0-9]' → Blocages")
    print(f"   - 'LABYRINTHE.*COULOIR.*erreur=[0-9]' → Centrage couloir")
    print(f"   - 'DEBLOCAGE.*PHASE' → Séquences déblocage")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    analyze_log()
