import random

from model.kwest import Kwest

# Zásoba všech kvestů: [název, popis, klíč počítadla, cíl, obtížnost 1–3]
# Klíče odpovídají počítadlům ve StatistikaHrace.
ZASOBA_KVESTU = [
    ["Lovec pěšců", "Seber 3 pěšce", "brani_Pěšák", 3, 1],
    ["Jezdecký útok", "Seber koněm 2 pěšce", "brani_Kůň_Pěšák", 2, 2],
    ["Korunovace", "Proměň pěšce v dámu", "promena", 1, 3],
    ["Velký lov", "Seber soupeři 5 figurek", "brani", 5, 2],
    ["Bezpečný král", "Udělej rošádu", "rosada", 1, 1],
    ["Útočník", "Dej soupeři 3× šach", "sach", 3, 2],
    ["Skok do šachu", "Dej šach koněm", "sach_Kůň", 1, 2],
    ["Šachová dáma", "Dej šach dámou", "sach_Dáma", 1, 1],
    ["Pád věže", "Seber soupeřovu věž", "brani_Věž", 1, 2],
    ["Lov na dámu", "Seber soupeřovu dámu", "brani_Dáma", 1, 3],
    ["Ostrostřelec", "Seber střelcem 2 figurky", "brani_figurkou_Střelec", 2, 2],
    ["Dámina síla", "Seber dámou 3 figurky", "brani_figurkou_Dáma", 3, 2],
    ["Král válečník", "Seber figurku králem", "brani_figurkou_Král", 1, 2],
    ["Pěšák hrdina", "Seber pěšcem 2 figurky", "brani_figurkou_Pěšák", 2, 1],
    ["Věž v akci", "Seber věží 2 figurky", "brani_figurkou_Věž", 2, 2],
    ["Pán středu", "Táhni 4× do středu (d4–e5)", "stred", 4, 1],
    ["Rychlý start", "Udělej 3× dvojkrok pěšcem", "dvojkrok", 3, 1],
    ["Převaha", "Seber figurky za 12 bodů", "hodnota", 12, 3],
    ["Koňská cesta", "Táhni koněm 6×", "tah_Kůň", 6, 1],
    ["Výlet krále", "Táhni králem 4×", "tah_Král", 4, 2],
    ["Lovec jezdců", "Seber soupeřova koně", "brani_Kůň", 1, 1],
    ["Lovec střelců", "Seber 2 střelce", "brani_Střelec", 2, 2],
    ["Vytrvalec", "Odehraj 20 tahů", "tahy", 20, 1],
    ["Průnik", "Pěšcem na předposlední řadu", "predposledni", 1, 2],
]


class KwestManager:
    def __init__(self):
        self.kvesty = []          # zásoba všech kvestů
        self.vytvor_zasobu()

    def vytvor_zasobu(self):
        # Z tabulky ZASOBA_KVESTU vytvoří objekty Kwest
        for radek in ZASOBA_KVESTU:
            kwest = Kwest(radek[0], radek[1], radek[2], radek[3], radek[4])
            if kwest.validate():
                self.pridej_kwest(kwest)

    def pridej_kwest(self, kwest):
        self.kvesty.append(kwest)

    def najdi_kwest(self, nazev):
        for kwest in self.kvesty:
            if kwest.nazev == nazev:
                return kwest
        return None

    def vyber_nahodne(self, pocet):
        # Náhodně vybere 'pocet' různých kvestů a vrátí jejich KOPIE
        vybrane = random.sample(self.kvesty, pocet)
        kopie = []
        for kwest in vybrane:
            kopie.append(kwest.kopie())
        return kopie

    def zkontroluj_kvesty(self, hrac):
        # Zkontroluje kvesty hráče a vrátí seznam těch, které právě splnil
        nove_splnene = []
        for kwest in hrac.kvesty:
            if not kwest.splneny and kwest.je_splneny(hrac.statistika):
                kwest.splneny = True
                hrac.uzivatel.pridej_kwest(kwest)   # uloží se uživateli
                nove_splnene.append(kwest)
        return nove_splnene
