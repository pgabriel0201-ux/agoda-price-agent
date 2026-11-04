import os
import json
from dotenv import load_dotenv
from groq import Groq
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=API_KEY)

def parser_message(message):
  annee_actuelle = datetime.now().year

  prompt = f"""Tu es un assistant qui extrait des informations de prix depuis un message en français.

Voici le message à analyser :
{message}

Nous sommes en l'année {annee_actuelle}.

Réponds UNIQUEMENT avec un objet JSON valide, sans aucun texte avant ou après, selon cette structure exacte :
{{
  "date_debut": "...",
  "date_fin": "...",
  "chambres": {{
    "weekend": {{"jours_habituels": [...], "dates_speciales": [...], "prix": ...}},
    "semaine": {{"prix": ...}}
  }},
  "maisons": [
    {{"nom": "...", "prix": ...}}
  ]
}}

Pour "date_debut" et "date_fin", utilise EXACTEMENT le format YYYY-MM-DD (année-mois-jour, avec des tirets), en te basant sur l'année {annee_actuelle} sauf si le message précise une autre année explicitement.

Pour "dates_speciales", n'inclus QUE des dates écrites explicitement dans le message. Si le message ne mentionne aucune date spéciale, n'invente rien et mets une liste vide [].

Si une section (chambres ou maisons) est absente du message, ne l'inclus pas dans le JSON.

Dans ce contexte (Vietnam), "WE" ou "weekend" signifie TOUJOURS vendredi et samedi, sauf si le message précise d'autres jours explicitement. Dans ce cas, "jours_habituels" vaut ["Vendredi", "Samedi"].

Tous les "prix" doivent être des nombres entiers en VND, sans guillemets, sans espaces ni séparateurs. La lettre "M" veut dire million : "1.6 M" ou "1,6 M" donne 1600000 et "1.8 M" donne 1800000. "888 000" donne 888000."""

  chat = client.chat.completions.create(
  messages=[{"role": "user", "content": prompt}],
  model="openai/gpt-oss-120b",
  temperature=0,
  max_tokens=1500
  )

  reponse_brute = chat.choices[0].message.content
    
  donnees = json.loads(reponse_brute)
    
  return donnees

if __name__ == "__main__":
    message_test = """Pourriez-vous changer à 1.6 M / nuit pour les jours de la semaine et 1.8 M par nuit pour les jours de WE à partir de 15/11/2026 à 22/11/2026 sur Agoda et les autres apps ?"""

    resultat = parser_message(message_test)
    print(resultat)