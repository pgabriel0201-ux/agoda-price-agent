from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from parser import parser_message
from playwright.async_api import async_playwright
from agoda_updater import connexion, _delai_humain, appliquer_prix_toutes_chambres, PROPRIETES
import os
import json
import time

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
                           

async def start(update, context):
    await update.message.reply_text("Salut je suis ton agent qui change les prix automatiquement")

async def gerer_message(update, context): 
    if "attente_confirmation" in context.user_data:
        if update.message.text == "OK":
            donnees = context.user_data["attente_confirmation"]

            if not donnees["blocs"]:
                await update.message.reply_text("Il n'y a rien à modifier")
                return

            noms_inconnus = []
            for bloc in donnees["blocs"]:
                if bloc["proprietes"] == ["TOUTES"]: 
                    bloc["proprietes"] = list(PROPRIETES)                                  

                for nom_propriete in bloc["proprietes"]:
                    if nom_propriete not in PROPRIETES:
                        noms_inconnus.append(nom_propriete)

            if noms_inconnus:
                await update.message.reply_text(f"Noms inconnus : {', '.join(noms_inconnus)}. Je ne touche à rien.")            
                return 


            async with async_playwright() as p:
                navigateur = await p.chromium.launch(headless=False)
                page = await navigateur.new_page()
                connecte = await connexion(page)
                print("connecte =", connecte)

                if connecte:  
                    await update.message.reply_text("Connexion réussie")

                    for bloc in donnees["blocs"]:
                        for nom_propriete in bloc["proprietes"]:
                            if bloc["semaine"]:
                                await appliquer_prix_toutes_chambres(page, nom_propriete, donnees["date_debut"], donnees["date_fin"], bloc["semaine"]["prix"], ["Mon", "Tue", "Wed", "Thu", "Sun"])
                                _delai_humain()
                            await appliquer_prix_toutes_chambres(page, nom_propriete, donnees["date_debut"], donnees["date_fin"], bloc["weekend"]["prix"], ["Fri", "Sat"])

                    del context.user_data["attente_confirmation"]
                    await update.message.reply_text("Les prix sont modifiés")
                
                else:
                    await update.message.reply_text("Connexion échouée")
                    time.sleep(15) 

    else:
        texte = update.message.text
        resultat = parser_message(texte)
        context.user_data["attente_confirmation"] = resultat
        await update.message.reply_text(json.dumps(resultat))
    
    
    

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, gerer_message))
app.run_polling()