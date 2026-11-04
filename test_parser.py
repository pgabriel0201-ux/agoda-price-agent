lignes_maison = [
    "BV 84 : 2 688 000 / jour",
    "BV 242 : 5 688 000 / jour",
    "CALMETTE : 6 688 000 / jour",
    "NTMK : 8 888 000 / jour"
]

resultats = []

for ligne in lignes_maison:
    morceaux = ligne.split(":")
    nom = morceaux[0].strip()
    
    reste = morceaux[1].strip()
    morceaux_prix = reste.split("/")
    prix_texte = morceaux_prix[0].strip()
    
    prix_nombre = int(prix_texte.replace(" ", ""))
    
    entree = {
        "nom": nom,
        "prix": prix_nombre,
    }
    resultats.append(entree)

#print(resultats)


message = """Pourriez-vous mettre les prix suivants :

I. PRIX du 05/09 au 24/09 AVEC commissions et taxes :

  * AUTRES APPS :
  + CHAMBRES : WE (Vendredi & Samedi + 02/09 + 03/09) : 999 000 VND
              Autres jours : 888 000 VND
  + MAISON :
    BV 84 : 2 688 000 / jour
    BV 242 : 5 688 000 / jour
    CALMETTE : 6 688 000 / jour
    NTMK : 8 888 000 / jour

MERCI DE ME TENIR AU COURANT, SVP"""

lignes = message.split("\n")

for ligne in lignes:
    if ":" in ligne:
        print(ligne)