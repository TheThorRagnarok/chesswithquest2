# trida reprezentujici hrace (rozšiřuje Uzivatele o barvu figur)

from model.statistika_hrace import StatistikaHrace


class Hrac:
    def __init__(self, barva, uzivatel):
        self.barva = barva                    # 0 = bílý, 1 = černý
        self.uzivatel = uzivatel
        self.kvesty = []                      # kvesty, které hráč v této partii plní
        self.statistika = StatistikaHrace()   # co hráč v partii udělal

    def getEloRating(self):
        return self.uzivatel.elo

    def pocet_splnenych_kvestu(self):
        pocet = 0
        for kwest in self.kvesty:
            if kwest.splneny:
                pocet = pocet + 1
        return pocet

    def splnil_vsechny_kvesty(self):
        return len(self.kvesty) > 0 and self.pocet_splnenych_kvestu() == len(self.kvesty)

    def __str__(self):
        barva_text = "Bílý" if self.barva == 0 else "Černý"
        return f"Hráč: {self.uzivatel.uzivatelske_jmeno} ({barva_text})"
