class Kwest:
    # Jeden úkol (kvest), který může hráč během partie splnit.
    # klic = jaké počítadlo ze StatistikaHrace sledujeme (např. "brani_Pěšák")
    # cil = kolik musí počítadlo dosáhnout (např. 3)
    # obtiznost = 1 až 3 (zobrazuje se jako hvězdičky)

    def __init__(self, nazev, popis, klic, cil, obtiznost):
        self.nazev = nazev
        self.popis = popis
        self.klic = klic
        self.cil = cil
        self.obtiznost = obtiznost
        self.splneny = False

    def validate(self):
        # Kvest je platný, pokud má název, popis a kladný cíl
        if self.nazev and self.popis and self.cil > 0:
            return True
        return False

    def zjisti_postup(self, statistika):
        # Kolik už hráč splnil (nejvýš cil, aby se nezobrazovalo např. 5/3)
        postup = statistika.hodnota(self.klic)
        if postup > self.cil:
            postup = self.cil
        return postup

    def postup_text(self, statistika):
        # např. "2/3"
        return str(self.zjisti_postup(statistika)) + "/" + str(self.cil)

    def je_splneny(self, statistika):
        return statistika.hodnota(self.klic) >= self.cil

    def kopie(self):
        # Nová kopie kvestu – každý hráč musí mít vlastní objekt,
        # jinak by si navzájem přepisovali, jestli je kvest splněný.
        return Kwest(self.nazev, self.popis, self.klic, self.cil, self.obtiznost)

    def __str__(self):
        return f"Kwest: {self.nazev}"
