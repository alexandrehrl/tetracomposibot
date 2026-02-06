import discord
from discord.ext import commands
import subprocess
import os
import re
import sys

# ================= CONFIGURATION =================
TOKEN = '' 
TARGET_CHANNEL_ID = 1468704612109258823
# =================================================

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

received_files = []

@bot.event
async def on_ready():
    print(f'Arbitre Paint Wars opérationnel.')
    channel = bot.get_channel(TARGET_CHANNEL_ID)
    if channel:
        await channel.send("⚔️ **Le combat va commencer, envoyez vos 2 fichiers de robots (.py) !**")

@bot.event
async def on_message(message):
    global received_files
    if message.author == bot.user:
        return

    if message.channel.id == TARGET_CHANNEL_ID and message.attachments:
        for attachment in message.attachments:
            if attachment.filename.endswith('.py'):
                received_files.append(attachment)
                
                if len(received_files) == 1:
                    await message.channel.send(f"✅ **Premier fichier reçu** : `{attachment.filename}`. Envoyez le second !")
                
                elif len(received_files) == 2:
                    await message.channel.send(f"✅ **Deuxième fichier reçu** : `{attachment.filename}`.")
                    await message.channel.send("⏳ **Le combat est en cours... Veuillez patienter et ne rien envoyer avant les résultats svp.**")
                    
                    await run_duel(message.channel)
                    received_files = [] 
                    break
    
    await bot.process_commands(message)

async def run_duel(channel):
    global received_files
    
    try:
        # 1. Sauvegarde propre des fichiers
        # On écrase les anciens fichiers pour éviter les résidus
        await received_files[0].save("robot_challenger.py")
        await received_files[1].save("robot_champion.py")

        all_stdout = ""
        
        # 2. Simulation (Boucle Windows)
        # On lance chaque match dans un nouveau processus pour isoler les robots
        for map_id in range(5):
            for init_pos in ["True", "False"]:
                # On force Python à ne pas utiliser de cache pyc pour éviter les conflits
                cmd = [sys.executable, "tetracomposibot.py", "config_Paintwars", str(map_id), init_pos, "2"]
                process = subprocess.run(cmd, capture_output=True, text=True, timeout=30, encoding='utf-8')
                all_stdout += process.stdout

        # 3. Extraction dynamique des noms et scores
        # Cette Regex capture n'importe quel nom d'équipe entre les crochets
        results = re.findall(r"\[\s*(.*?)\s*=>\s*(\d+)\s*\]\s*\[\s*(.*?)\s*=>\s*(\d+)\s*\]", all_stdout)

        if not results:
            await channel.send("⚠️ **Erreur** : Impossible de lire les noms d'équipes ou les scores. Vérifiez que vos fichiers définissent bien `team_name`.")
            return

        # 4. Préparation de l'affichage
        name1 = results[0][0]
        name2 = results[0][2]
        
        embed = discord.Embed(title="🏆 Résultats du Duel Paint Wars", color=discord.Color.gold())
        
        total_challenger = 0
        total_champion = 0
        arena_scores = {}

        for idx, res in enumerate(results):
            arena_id = idx // 2
            s1, s2 = int(res[1]), int(res[3])
            total_challenger += s1
            total_champion += s2
            
            if arena_id not in arena_scores:
                arena_scores[arena_id] = [0, 0]
            arena_scores[arena_id][0] += s1
            arena_scores[arena_id][1] += s2

        for a_id, scores in arena_scores.items():
            embed.add_field(
                name=f"📍 Arène {a_id}", 
                value=f"**{name1}**: {scores[0]} pts\n**{name2}**: {scores[1]} pts", 
                inline=True
            )

        winner_text = "Égalité !"
        if total_challenger > total_champion:
            winner_text = f"🥇 Victoire de **{name1}** !"
        elif total_champion > total_challenger:
            winner_text = f"🥇 Victoire de **{name2}** !"

        embed.description = f"**{winner_text}**\nScore total : **{total_challenger}** - **{total_champion}**"
        
        await channel.send(embed=embed)
        await channel.send("\n🔄 *Prêt pour un nouveau combat ? Envoyez vos 2 fichiers !*")

    except subprocess.TimeoutExpired:
        await channel.send("⏰ **Erreur** : Temps limite dépassé (boucle infinie dans un robot).")
    except Exception as e:
        print(f"Erreur : {e}")
        await channel.send("⚙️ **Erreur technique** lors du duel.")

if __name__ == "__main__":
    bot.run(TOKEN)