def appliquer_prix_toutes_chambres(page, nom_propriete, date_debut, date_fin, prix, jours_a_garder):

    _delai_humain()
    naviguer_vers_calendrier(page, nom_propriete, "chambres", date_debut, date_fin)

    _delai_humain()
    page.locator(SELECTEUR_MENU_CHAMBRES).click()
    _delai_humain()
    page.locator(SELECTEUR_SELECT_ALL).wait_for()
    page.locator(SELECTEUR_SELECT_ALL).click()
    _delai_humain()
    page.locator(SELECTEUR_APPLY_ALL).click()

    jours_a_garder = jours_a_garder
    for jour in JOURS_SEMAINE:
        if jour not in jours_a_garder:
            SELECTEUR_JOURS_DECOCHES = f"[data-testid='day-of-week-accordion-{JOURS_SEMAINE[jour]}']"
            _delai_humain()
            page.locator(SELECTEUR_JOURS_DECOCHES).click()
    
    for nom_chambre, id_chambre in PROPRIETES[nom_propriete]["chambres_ids"].items():
        SELECTEUR_TOGGLE = f"[data-testid='ycs-calendar-page-room-card-accordion-toggle-{id_chambre}']"
        _delai_humain()
        page.locator(SELECTEUR_TOGGLE).click()

        SELECTEUR_PRIX = f"[data-testid='rate-card-input-{id_chambre}-{ID_RATE_PLAN}']"
        page.locator(SELECTEUR_PRIX).wait_for()
        _delai_humain()
        page.locator(SELECTEUR_PRIX).click()
        _delai_humain()
        page.locator(SELECTEUR_PRIX).press("Control+A")
        _delai_humain()
        page.locator(SELECTEUR_PRIX).press_sequentially(prix)
        try: 
            _delai_humain()
            page.locator(SELECTEUR_BOUTON_SAVE).click(timeout=2000)
        except:
            pass