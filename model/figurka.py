# Základní třída pro všechny šachové figurky

class Figurka:
    def __init__(self, nazev, barva, vektory_utoku, vektory):
        self.nazev = nazev
        self.vektory_utoku = vektory_utoku
        self.barva = barva              # 0 = bílá, 1 = černá
        self.vektory = vektory
        self.pozice = None              # [radek, sloupec]

        # skok = True  -> figurka přeskakuje ostatní (kůň)
        # opakovat = True -> figurka jde ve směru vektoru libovolně daleko
        #                    (dáma, věž, střelec); král, kůň a pěšák jdou jen o jeden krok
        self.skok = False
        self.opakovat = False

        # písmeno figurky v šachové notaci (K, Q, R, B, N; pěšák nemá žádné)
        self.znacka = ""

        # kolikrát už figurka táhla (potřeba pro rošádu a dvojkrok pěšce)
        self.pocet_tahu = 0

    def get_pozice(self):
        # Vrátí aktuální pozici figurky
        return self.pozice

    def posun_figurky(self, seznam):
        # Posune figurku o vektor [radek, sloupec]
        if seznam and len(seznam) == 2:
            if self.pozice is not None:
                novy_radek = self.pozice[0] + seznam[0]
                novy_sloupec = self.pozice[1] + seznam[1]
                self.pozice = [novy_radek, novy_sloupec]
        return self.pozice

    def __str__(self):
        barva_text = "bílá" if self.barva == 0 else "černá"
        return f"{self.nazev} ({barva_text}) na {self.pozice}"
