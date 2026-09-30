from model.kral import Kral
from model.pesak import Pesak
from model.dama import Dama


class Tah:
    def __init__(self, vychozi_pozice, cilova_pozice, figurka, typ_tahu):
        self.vychozi_pozice = vychozi_pozice
        self.cilova_pozice = cilova_pozice
        self.figurka = figurka
        self.typ_tahu = typ_tahu          # "normalni", "brani", "rosada"
        self.vyhozena_figurka = None      # figurka, kterou tah sebral
        self.promena = False              # True, pokud se pěšák proměnil v dámu

    def over_platnost(self):
        # Kontroluje jen to, že obě pozice leží na desce.
        # Pravidla šachu kontroluje RevizorTahu.
        for pozice in [self.vychozi_pozice, self.cilova_pozice]:
            for souradnice in pozice:
                if not (0 <= souradnice < 8):
                    return False
        return True

    def proved_tah(self, herni_plocha):
        # Provede tah na herní ploše (tah už musí být ověřený RevizoremTahu)
        cil = herni_plocha.vrat_obsah(self.cilova_pozice)

        # 1) braní – sebranou figurku dáme mezi vyhozené
        if cil is not None:
            self.vyhozena_figurka = cil
            self.typ_tahu = "brani"
            if cil.barva == 0:
                herni_plocha.vyhozene_figurky_b.append(cil)
            else:
                herni_plocha.vyhozene_figurky_c.append(cil)

        # 2) přesun figurky
        herni_plocha.odeber_figurku(self.vychozi_pozice)
        herni_plocha.poloz_figurku(self.figurka, self.cilova_pozice)
        self.figurka.pocet_tahu += 1

        # 3) rošáda – král jde o 2 pole do strany, věž přeskočí přes něj
        posun_sloupcu = self.cilova_pozice[1] - self.vychozi_pozice[1]
        if isinstance(self.figurka, Kral) and (posun_sloupcu == 2 or posun_sloupcu == -2):
            self.typ_tahu = "rosada"
            radek = self.vychozi_pozice[0]
            if posun_sloupcu == 2:
                # krátká rošáda: věž z h na f
                vez = herni_plocha.odeber_figurku([radek, 7])
                herni_plocha.poloz_figurku(vez, [radek, 5])
            else:
                # dlouhá rošáda: věž z a na d
                vez = herni_plocha.odeber_figurku([radek, 0])
                herni_plocha.poloz_figurku(vez, [radek, 3])
            vez.pocet_tahu += 1

        # 4) proměna pěšáka – na poslední řadě se z něj stane dáma
        if isinstance(self.figurka, Pesak):
            if self.cilova_pozice[0] == 0 or self.cilova_pozice[0] == 7:
                dama = Dama(self.figurka.barva)
                dama.pocet_tahu = self.figurka.pocet_tahu
                herni_plocha.poloz_figurku(dama, self.cilova_pozice)
                self.promena = True

        print(f"Tah proveden: {self.vychozi_pozice} -> {self.cilova_pozice}")

    def pole_na_text(self, souradnice):
        # [6, 4] -> "e2"
        pismena = "abcdefgh"
        return pismena[souradnice[1]] + str(8 - souradnice[0])

    def na_notaci(self):
        # Vrátí tah v dlouhé algebraické notaci, např. "e2-e4", "Ng1-f3", "e4xd5", "O-O"
        if self.typ_tahu == "rosada":
            if self.cilova_pozice[1] == 6:
                return "O-O"
            return "O-O-O"

        text = self.figurka.znacka + self.pole_na_text(self.vychozi_pozice)
        if self.vyhozena_figurka is not None:
            text = text + "x"
        else:
            text = text + "-"
        text = text + self.pole_na_text(self.cilova_pozice)
        if self.promena:
            text = text + "=Q"
        return text

    def __str__(self):
        barva_text = "bílý" if self.figurka.barva == 0 else "černý"
        return f"{barva_text}: {self.na_notaci()} ({self.figurka.nazev})"
