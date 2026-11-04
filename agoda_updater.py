import os
import random 
import time
import asyncio
import imaplib
import email
import re
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from html import unescape

load_dotenv()
AGODA_ID = os.getenv("AGODA_USERNAME")
AGODA_PASSWORD = os.getenv("AGODA_PASSWORD")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

SELECTEUR_EMAIL = '[data-cy="unified-email-input"]'
SELECTEUR_BOUTON_CONTINUER = '[data-cy="unified-email-continue-button"]'
SELECTEUR_USE_PASSWORD = '[data-cy="unified-auth-otp-use-password-button"]'
SELECTEUR_MOT_DE_PASSE = '[data-cy="password"]'
SELECTEUR_BOUTON_CONNEXION = '[data-cy="signin-button"]'
SELECTEUR_BOUTON_CROIX = '[aria-label="close"]'
SELECTEUR_BOUTON_SAVE = '[data-testid="ycs-calendar-update-button"]'
SELECTEUR_IFRAME = '[data-cy="ul-app-frame"]'
SELECTEUR_MENU_CHAMBRES = '[data-testid="ycs-calendar-page-room-filter-button"]'
SELECTEUR_SELECT_ALL = '[data-testid="ycs-calendar-page-room-filter-select-all"]'
SELECTEUR_APPLY_ALL = '[data-testid="ycs-calendar-page-room-filter-apply-button"]'

PROPRIETES = {
    "NTMK": {
        "chambres": 64460441,
        "maison": 87934925,
        "rate_plan": 19443213,
        "chambres_ids": {
        "RDC": 1000014828,
        "1er_devant": 1000018669,
        "2eme_devant": 1000077213,
        "3eme_devant": 1000078702,
        "4eme_devant": 1000085136,
        "4eme_derriere": 1000085487,
        "3eme_derriere": 1000086798,
        "2eme_derriere": 1000086898,
        "1er_derriere": 1000086932
        }

    },
    "CALMETTE": {
        "chambres": 80606874,
        "maison": 76958683,
        "rate_plan": 22042465,
        "chambres_ids": {
        "302": 1266541211,
        "202": 1266541212,
        "301": 1266541213,
        "201": 1266541214,
        "101": 1266541215,
        "001": 1266541216,
        "102": 1266541217
        }
  
    },
    "BV_84": {
        "chambres": 86497055,
        "maison": 86736085,
        "rate_plan": 22966719,
        "chambres_ids": {
        "5": 1355752106,
        "1er_etage": 1359243940,
        "2eme_etage": 1359312533,
        "RDC": 1365244968
    }

    },
    "BV_242": {
        "chambres": 72310904,
        "maison": 76958707,
        "rate_plan": 20580642,
        "chambres_ids": {
        "202": 1139264788,
        "101": 1139264790,
        "302": 1139264791,
        "301": 1139264792
    }
    }
}

JOURS_SEMAINE = {
    "Mon": 1,
    "Tue": 2,
    "Wed": 3,
    "Thu": 4,
    "Fri": 5,
    "Sat": 6,
    "Sun": 7
}

def _delai_humain():
    secondes = random.uniform(1, 3)
    time.sleep(secondes)

def compter_emails_agoda():
    boite = imaplib.IMAP4_SSL("imap.gmail.com")
    boite.login(AGODA_ID, GMAIL_APP_PASSWORD)
    boite.select("INBOX")
    statut, donnees = boite.search(None, '(FROM "no-reply@account.agoda.com")')
    nb = len(donnees[0].split())
    boite.logout()
    return nb

def attendre_lien_connexion(nb_avant):
    boite = imaplib.IMAP4_SSL("imap.gmail.com")
    boite.login(AGODA_ID, GMAIL_APP_PASSWORD)
    boite.select("INBOX")
    delai_max = 60
    debut = time.time()
    dernier = None
    lien_connexion = None
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
        for partie in msg.walk():
            if partie.get_content_type() == "text/html":
                charset = partie.get_content_charset() or "utf-8"
                html = partie.get_payload(decode=True).decode(charset)
                liens = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
                for lien, texte in liens:
                    texte_propre = re.sub(r"<[^>]+>", "", texte).strip()
                    if texte_propre == "Sign-in link":
                        lien_connexion = unescape(lien)
                if lien_connexion:
                    print("Lien de connexion trouvé, longueur :", len(lien_connexion))
                else:
                    print("Aucun lien 'Sign-in link' trouvé")
    boite.logout()
    return lien_connexion

async def connexion(page):
    await page.goto("https://portal.agoda.com/mldc/en-us/public/login?")
    frame = page.frame_locator(SELECTEUR_IFRAME)
    nb_avant = compter_emails_agoda()

    await frame.locator(SELECTEUR_EMAIL).wait_for()
    await frame.locator(SELECTEUR_EMAIL).fill(AGODA_ID)

    await frame.locator(SELECTEUR_BOUTON_CONTINUER).wait_for()
    _delai_humain()
    await frame.locator(SELECTEUR_BOUTON_CONTINUER).click()

    try: 
        await frame.locator(SELECTEUR_USE_PASSWORD).click(timeout=8000)
        _delai_humain()
        await frame.locator(SELECTEUR_MOT_DE_PASSE).fill(AGODA_PASSWORD)
        _delai_humain()
        await frame.locator(SELECTEUR_BOUTON_CONNEXION).click()
    
        return True
    except:

        lien = attendre_lien_connexion(nb_avant)

        if lien is None:
            return False
        else:
            _delai_humain()
            await page.goto(lien)
            return True
    

async def naviguer_et_fermer_popup(page, url):
    await page.goto(url)
    try:
        _delai_humain()
        await page.locator(SELECTEUR_BOUTON_CROIX).click(timeout=5000)
    except:
        pass

async def naviguer_vers_calendrier(page, nom_propriete, type_bien, date_debut, date_fin):
    url = f"https://portal.agoda.com/mldc/en-us/app/ari/calendar/{PROPRIETES[nom_propriete][type_bien]}?startDate={date_debut}&endDate={date_fin}"
    await naviguer_et_fermer_popup(page, url)

async def appliquer_prix_toutes_chambres(page, nom_propriete, date_debut, date_fin, prix, jours_a_garder):

    _delai_humain()
    await naviguer_vers_calendrier(page, nom_propriete, "chambres", date_debut, date_fin)

    _delai_humain()
    await page.locator(SELECTEUR_MENU_CHAMBRES).click()
    _delai_humain()
    await page.locator(SELECTEUR_SELECT_ALL).wait_for()
    await page.locator(SELECTEUR_SELECT_ALL).click()
    _delai_humain()
    await page.locator(SELECTEUR_APPLY_ALL).click()

    _delai_humain()
    await page.locator("text=Specify day of the week").click()

    for jour in JOURS_SEMAINE:
        if jour not in jours_a_garder:
            SELECTEUR_JOURS_DECOCHES = f"[data-testid='day-of-week-accordion-{JOURS_SEMAINE[jour]}']"
            _delai_humain()
            await page.locator(SELECTEUR_JOURS_DECOCHES).click()

    id_rate_plan = PROPRIETES[nom_propriete]["rate_plan"]
    
    for nom_chambre, id_chambre in PROPRIETES[nom_propriete]["chambres_ids"].items():
        SELECTEUR_TOGGLE = f"[data-testid='ycs-calendar-page-room-card-accordion-toggle-{id_chambre}']"
        _delai_humain()
        await page.locator(SELECTEUR_TOGGLE).click()

        SELECTEUR_PRIX = f"[data-testid='rate-card-input-{id_chambre}-{id_rate_plan}']"
        await page.locator(SELECTEUR_PRIX).wait_for()
        _delai_humain()
        await page.locator(SELECTEUR_PRIX).click()
        _delai_humain()
        await page.locator(SELECTEUR_PRIX).press("Control+A")
        _delai_humain()
        await page.locator(SELECTEUR_PRIX).press_sequentially(str(prix))
        try: 
            _delai_humain()
            await page.locator(SELECTEUR_BOUTON_SAVE).click(timeout=2000)
        except:
            pass
    



async def main():
    async with async_playwright() as p:
        navigateur = await p.chromium.launch(headless=False)
        page = await navigateur.new_page() 
        await connexion(page)
        await appliquer_prix_toutes_chambres(page, "NTMK", "2026-09-22", "2026-09-27 ", "888000", ["Mon", "Tue", "Wed", "Thu", "Sun"])

        _delai_humain()

        await appliquer_prix_toutes_chambres(page, "NTMK", "2026-09-22", "2026-09-27", "999000", ["Fri", "Sat"])

        time.sleep(15)


if __name__ == "__main__": 
    asyncio.run(main())


