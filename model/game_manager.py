class GameManager:
    def __init__(self, plocha, hrac1, hrac2, game_logger, revizor_tahu, casovac):
        self.plocha = plocha
        self.aktivni_hrac = 0            # 0 = bílý, 1 = černý
        self.hraci = [hrac1, hrac2]      # hraci[0] je bílý, hraci[1] černý
        self.aktualni_tah = None
        self.casovac = casovac
        self.game_logger = game_logger
        self.revizor_tahu = revizor_tahu

    def proved_tah(self):
        # Ověří aktuální tah přes RevizorTahu, provede ho a uloží do logu
        if self.aktualni_tah is None:
            return False
        if not self.revizor_tahu.over_tah(self.aktualni_tah):
            return False
        self.aktualni_tah.proved_tah(self.plocha)
        self.game_logger.uloz_tah(self.aktualni_tah)
        return True

    def zacni_tah(self, figurka):
        # Vrátí seznam polí, kam může figurka táhnout
        mozne = []
        if self.revizor_tahu:
            mozne = self.revizor_tahu.simuluj_move(figurka, self.plocha)
        return mozne

    def mozne_tahy(self, tah):
        # Nastaví tah, který se bude provádět
        self.aktualni_tah = tah

    def zrus_tah(self):
        self.aktualni_tah = None

    def prepni_hrace(self):
        # Na tahu je druhý hráč, čas teď běží jemu
        self.aktivni_hrac = 1 - self.aktivni_hrac
        if self.casovac is not None:
            self.casovac.prepni_hrace(self.aktivni_hrac)

    def get_aktivni_hrac(self):
        return self.hraci[self.aktivni_hrac]

    def get_souper(self):
        return self.hraci[1 - self.aktivni_hrac]

    def uloz_log(self, text):
        # Uloží celý zápis partie na konec souboru
        self.game_logger.uloz_text(text)
        print("Log hry uložen.")

    def get_stav(self):
        # 0 = hra běží, 1 = šach, 2 = mat, 3 = pat (pro hráče na tahu)
        barva = self.aktivni_hrac
        if self.revizor_tahu.check_mat(barva, self.plocha):
            return 2
        if self.revizor_tahu.check_pat(barva, self.plocha):
            return 3
        if self.revizor_tahu.check_sach(barva, self.plocha):
            return 1
        return 0

    def najdi_uzivatele(self, uzivatelske_jmeno):
        for hrac in self.hraci:
            if hrac.uzivatel.uzivatelske_jmeno == uzivatelske_jmeno:
                return hrac.uzivatel
        return None

    def __str__(self):
        return f"GameManager – aktivní hráč: {self.aktivni_hrac}"
