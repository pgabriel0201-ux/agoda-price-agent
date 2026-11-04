# test_gmail.py : test isolé de la lecture de l'email Agoda
import os
import re
import imaplib
import email
import time
from html import unescape
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()
AGODA_ID = os.getenv("AGODA_USERNAME")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# 1. Connexion à la boîte
boite = imaplib.IMAP4_SSL("imap.gmail.com")
boite.login(AGODA_ID, GMAIL_APP_PASSWORD)
boite.select("INBOX")
statut, donnees = boite.search(None, '(FROM "no-reply@account.agoda.com")')
numeros = donnees[0].split()
nb_avant= len(numeros)
delai_max = 60
debut = time.time()
dernier = None

while time.time() - debut < delai_max:
    boite.select("INBOX")
    statut, donnees = boite.search(None, '(FROM "no-reply@account.agoda.com")')
    numeros = donnees[0].split()
    print("avant :", nb_avant, "| maintenant :", len(numeros), "| secondes :", int(time.time() - debut))
    if len(numeros) > nb_avant: 
        dernier = numeros[-1]
        break
    else:
        time.sleep(3)

if dernier is None:
    print("Aucun nouvel email reçu en 60 secondes")


else: 
    statut, contenu = boite.fetch(dernier, "(RFC822)")
    msg = email.message_from_bytes(contenu[0][1])
    print("Objet :", msg["Subject"])
    print("Date  :", msg["Date"])
    lien_connexion = None
    # 4. Recherche des liens dans la partie HTML

    for partie in msg.walk():
        if partie.get_content_type() == "text/html":
            charset = partie.get_content_charset() or "utf-8"
            html = partie.get_payload(decode=True).decode(charset)
            liens = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
            print(f"{len(liens)} lien(s) trouvé(s)")
           
            for lien, texte in liens:
                texte_propre = re.sub(r"<[^>]+>", "", texte).strip()
                if texte_propre == "Sign-in link":
                    lien_connexion = unescape(lien)

            if lien_connexion:
                print("Lien de connexion trouvé, longueur :", len(lien_connexion))
            else:
                print("Aucun lien 'Sign-in link' trouvé")

boite.logout()