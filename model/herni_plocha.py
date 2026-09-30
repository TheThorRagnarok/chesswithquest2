class HerniPlocha:
    def __init__(self):
        self.rozmery = (8, 8)
        self.herni_deska = []            # herni_deska[radek][sloupec]
        self.vyhozene_figurky_b = []     # vyhozené bílé figurky
        self.vyhozene_figurky_c = []     # vyhozené černé figurky

        for radek in range(8):
            self.herni_deska.append([None] * 8)

    def je_na_desce(self, souradnice):
        # Vrátí True, pokud souřadnice leží na šachovnici
        radek, sloupec = souradnice
        return 0 <= radek < 8 and 0 <= sloupec < 8

    def vrat_obsah(self, souradnice):
        # Vrátí figurku na poli (nebo None, když je pole prázdné nebo mimo desku)
        if self.je_na_desce(souradnice):
            radek, sloupec = souradnice
            return self.herni_deska[radek][sloupec]
        return None

    def poloz_figurku(self, figurka, souradnice):
        radek, sloupec = souradnice
        self.herni_deska[radek][sloupec] = figurka
        figurka.pozice = [radek, sloupec]

    def odeber_figurku(self, souradnice):
        # Odebere figurku z pole a vrátí ji
        radek, sloupec = souradnice
        figurka = self.herni_deska[radek][sloupec]
        self.herni_deska[radek][sloupec] = None
        return figurka

    def vsechny_figurky(self, barva):
        # Vrátí seznam všech figurek dané barvy, které jsou na desce
        figurky = []
        for radek in range(8):
            for sloupec in range(8):
                figurka = self.herni_deska[radek][sloupec]
                if figurka is not None and figurka.barva == barva:
                    figurky.append(figurka)
        return figurky

    def __str__(self):
        return f"HerniPlocha {self.rozmery}"
