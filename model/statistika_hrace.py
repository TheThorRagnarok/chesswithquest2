# Statistika jednoho hráče během partie.
# Po každém tahu se do ní připíše, co se v tahu stalo (braní, šach, rošáda...).
# Kvesty se pak jen ptají: "kolik už má hráč v počítadle X?"

# Hodnota figurek v bodech (klasické šachové hodnocení)
HODNOTY_FIGUREK = {
    "Pěšák": 1,
    "Kůň": 3,
    "Střelec": 3,
    "Věž": 5,
    "Dáma": 9,
    "Král": 0,
}

# Čtyři středová pole d5, e5, d4, e4 jako [radek, sloupec]
STREDOVA_POLE = [[3, 3], [3, 4], [4, 3], [4, 4]]


class StatistikaHrace:
    def __init__(self):
        # slovník počítadel, např. {"tahy": 12, "brani": 3, "brani_Pěšák": 2}
        self.pocitadla = {}

    def hodnota(self, klic):
        # Vrátí stav počítadla (0, pokud ještě neexistuje)
        if klic in self.pocitadla:
            return self.pocitadla[klic]
        return 0

    def pricti(self, klic, kolik):
        self.pocitadla[klic] = self.hodnota(klic) + kolik

    def zaznamenej_tah(self, tah, dal_sach, sachujici_figurka):
        # Zapíše do počítadel všechno, co se v provedeném tahu stalo.
        # dal_sach = True, pokud je soupeřův král po tahu v šachu
        # sachujici_figurka = název figurky, která šach dává (nebo None)
        nazev = tah.figurka.nazev

        # každý tah a tahy jednotlivými figurkami
        self.pricti("tahy", 1)
        self.pricti("tah_" + nazev, 1)

        # braní
        if tah.vyhozena_figurka is not None:
            obet = tah.vyhozena_figurka.nazev
            self.pricti("brani", 1)                           # sebral cokoliv
            self.pricti("brani_" + obet, 1)                   # sebral např. pěšce
            self.pricti("brani_figurkou_" + nazev, 1)         # bral např. koněm
            self.pricti("brani_" + nazev + "_" + obet, 1)     # kůň sebral pěšce
            self.pricti("hodnota", HODNOTY_FIGUREK[obet])     # body za sebrané figurky

        # speciální tahy
        if tah.promena:
            self.pricti("promena", 1)
        if tah.typ_tahu == "rosada":
            self.pricti("rosada", 1)

        # pěšák: dvojkrok a průnik na předposlední řadu
        if nazev == "Pěšák":
            posun = tah.cilova_pozice[0] - tah.vychozi_pozice[0]
            if posun == 2 or posun == -2:
                self.pricti("dvojkrok", 1)
            if tah.figurka.barva == 0:
                predposledni_rada = 1       # bílý jde nahoru (k řádku 0)
            else:
                predposledni_rada = 6       # černý jde dolů (k řádku 7)
            if tah.cilova_pozice[0] == predposledni_rada:
                self.pricti("predposledni", 1)

        # tah do středu šachovnice
        if tah.cilova_pozice in STREDOVA_POLE:
            self.pricti("stred", 1)

        # šach
        if dal_sach:
            self.pricti("sach", 1)
            if sachujici_figurka is not None:
                self.pricti("sach_" + sachujici_figurka, 1)
