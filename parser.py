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
  "blocs": [
    {{
      "proprietes": ["..."],
      "weekend": {{"jours_habituels": [...], "dates_speciales": [...], "prix": ...}},
      "semaine": {{"prix": ...}}
    }}
  ],
  "maisons": [
    {{"nom": "...", "prix": ...}}
  ]
}}

Pour "date_debut" et "date_fin", utilise EXACTEMENT le format YYYY-MM-DD (année-mois-jour, avec des tirets), en te basant sur l'année {annee_actuelle} sauf si le message précise une autre année explicitement.

Pour "dates_speciales", n'inclus QUE des dates écrites explicitement dans le message. Si le message ne mentionne aucune date spéciale, n'invente rien et mets une liste vide [].

Si le message donne un prix différent pour des dates spéciales, mets ce prix dans "prix_dates_speciales". S'il n'y a pas de dates spéciales, mets null.

Dans ce contexte (Vietnam), "WE" ou "weekend" signifie TOUJOURS vendredi et samedi, sauf si le message précise d'autres jours explicitement. Dans ce cas, "jours_habituels" vaut ["Vendredi", "Samedi"].

Si le message donne un seul prix sans distinguer semaine et weekend, mets ce même prix dans "semaine" et dans "weekend".

Si le message ne donne un prix que pour le weekend, mets "semaine" à null et remplis "weekend" normalement.

Tous les "prix" doivent être des nombres entiers en VND, sans guillemets, sans espaces ni séparateurs. La lettre "M" veut dire million : "1.6 M" ou "1,6 M" donne 1600000 et "1.8 M" donne 1800000. "888 000" donne 888000.

Pour "proprietes" dans chaque bloc, utilise UNIQUEMENT ces noms :
- "NTMK"
- "CALMETTE" (quelle que soit la casse)
- "BV_84" si le message écrit "BV 84", "BV84", "Bui Vien 84" ou "84 Bui Vien" ou juste ces mentions là en majuscule ou minuscule
- "BV_242" si le message écrit "BV 242", "BV242", "Bui Vien 242" ou "242 Bui Vien" ou juste ces mentions là en majuscule ou minuscule
Si le message mentionne "BV" ou "Bui Vien" avec un autre numéro, ou sans numéro, ne choisis aucune de ces propriétés : recopie le nom exactement comme il est écrit dans le message.
Si le message ne cite aucune propriété pour ces prix, mets ["TOUTES"].
Si plusieurs propriétés ont les mêmes prix, mets-les dans le même bloc. Si les prix diffèrent, fais un bloc par groupe de prix.

Les "maisons" et les "chambres" sont deux choses différentes. Remplis "maisons" uniquement si le message parle de maison(s), et mets alors une liste vide [] dans "blocs", sauf si le message donne aussi des prix pour les chambres. Ne mets jamais le même prix à la fois dans "blocs" et dans "maisons".

Pour "nom" dans "maisons", utilise UNIQUEMENT les mêmes noms que pour "proprietes" : "NTMK", "CALMETTE", "BV_84" ou "BV_242", avec les mêmes variantes d'écriture. Si le message écrit un autre nom, recopie-le tel quel.

Si une section (blocs ou maisons) est absente du message, mets une liste vide []."""

  chat = client.chat.completions.create(
  messages=[{"role": "user", "content": prompt}],
  model="openai/gpt-oss-120b",
  temperature=0,
  max_tokens=4000
  )

  reponse_brute = chat.choices[0].message.content

  donnees = json.loads(reponse_brute)
    
  return donnees

if __name__ == "__main__":
    message_test = """Pour le 10/04/2027,pour les maisons BV 84 : 15199000 / jour, BV 242 : 8999000 / jour, NTMK: 24599000/jour et Calmette: 18399000/jour"""

    resultat = parser_message(message_test)
    print(resultat)