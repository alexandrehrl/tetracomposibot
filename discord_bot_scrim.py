TOKEN = '' 

import discord
from discord.ext import commands
import subprocess
import os
import re
import sys

# ================= CONFIGURATION =================
TARGET_CHANNEL_ID = 1468704612109258823
# =================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

received_files = [] 

def get_team_name_from_file(file_path, default_name):
    """Lit le fichier pour trouver la variable team_name = '...' """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Cherche team_name = "Nom" ou team_name = 'Nom'
            match = re.search(r'team_name\s*=\s*["\'](.*?)["\']', content)
            if match:
                return match.group(1)
    except Exception as e:
        print(f"Erreur lecture nom : {e}")
    return default_name

@bot.event
async def on_ready():
    print(f'Arbitre Paint Wars opérationnel.')

@bot.event
async def on_message(message):
    global received_files
    if message.author == bot.user or message.channel.id != TARGET_CHANNEL_ID:
        return

    if message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith('.py'):
                received_files.append((attachment, message))
                
                if len(received_files) == 1:
                    await message.channel.send(f"✅ **Premier fichier reçu** : `{attachment.filename}`.")
                
                elif len(received_files) == 2:
                    await message.channel.send("⏳ **Préparation du combat...**")
                    
                    # 1. Sauvegarde
                    await received_files[0][0].save("robot_challenger.py")
                    await received_files[1][0].save("robot_champion.py")

                    # 2. Extraction des VRAIS noms avant suppression
                    name1 = get_team_name_from_file("robot_challenger.py", "Challenger")
                    name2 = get_team_name_from_file("robot_champion.py", "Champion")

                    # 3. Suppression des messages
                    for _, msg_obj in received_files:
                        try:
                            await msg_obj.delete()
                        except:
                            pass
                    
                    await message.channel.send(f"🔒 **Fichiers de `{name1}` et `{name2}` protégés.** Lancement du duel...")
                    
                    await run_duel(message.channel, name1, name2)
                    received_files = [] 
                    break

async def run_duel(channel, real_name1, real_name2):
    try:
        all_stdout = ""
        for map_id in range(5):
            for init_pos in ["True", "False"]:
                cmd = [sys.executable, "tetracomposibot.py", "config_Paintwars", str(map_id), init_pos, "2"]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding='utf-8')
                
                # On ne garde que les lignes contenant les scores numériques
                clean_lines = [line for line in process.stdout.split('\n') if "=>" in line and "[" in line]
                all_stdout += "\n".join(clean_lines)

        # Extraction des scores (on ne prend que les chiffres ici, les noms sont déjà récupérés)
        results = re.findall(r"\[.*?=>\s*(\d+)\s*\]\s*\[.*?=>\s*(\d+)\s*\]", all_stdout)

        if not results:
            await channel.send("⚠️ Erreur : Les robots n'ont pas produit de scores valides.")
            return

        embed = discord.Embed(title="🏆 Résultats du Duel Paint Wars", color=discord.Color.gold())
        
        total1, total2 = 0, 0
        arena_scores = {}
        for idx, res in enumerate(results):
            a_id = idx // 2
            s1, s2 = int(res[0]), int(res[1])
            total1 += s1
            total2 += s2
            if a_id not in arena_scores: arena_scores[a_id] = [0, 0]
            arena_scores[a_id][0] += s1
            arena_scores[a_id][1] += s2

        for a_id, scores in arena_scores.items():
            embed.add_field(
                name=f"📍 Arène {a_id}", 
                value=f"**{real_name1}**: {scores[0]} pts\n**{real_name2}**: {scores[1]} pts", 
                inline=True
            )

        winner = f"🥇 Victoire de **{real_name1}** !" if total1 > total2 else f"🥇 Victoire de **{real_name2}** !"
        if total1 == total2: winner = "Égalité !"
        
        embed.description = f"**{winner}**\nScore total : **{total1}** - **{total2}**"
        await channel.send(embed=embed)
        await channel.send("\n🔄 *Envoyez 2 nouveaux fichiers pour un autre duel !*")

    except Exception as e:
        await channel.send(f"⚙️ Erreur technique : {e}")

bot.run(TOKEN)