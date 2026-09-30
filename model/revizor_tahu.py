from model.kral import Kral
from model.pesak import Pesak
from model.vez import Vez


class RevizorTahu:
    def __init__(self, herni_plocha, tah):
        self.herni_plocha = herni_plocha    # odkaz na HerniPlocha
        self.tah = tah                      # tah ke kontrole (může být None)

    # ------------------------------------------------------------------
    # Pomocné metody
    # ------------------------------------------------------------------

    def pole_ve_smeru(self, figurka, vektor, herni_plocha):
        # Vrátí seznam polí, kam figurka dosáhne v jednom směru (vektoru).
        # Zastaví se na okraji desky, před vlastní figurkou
        # nebo na cizí figurce (tu může sebrat).
        vysledek = []
        radek = figurka.pozice[0]
        sloupec = figurka.pozice[1]

        while True:
            radek = radek + vektor[0]
            sloupec = sloupec + vektor[1]

            if not herni_plocha.je_na_desce([radek, sloupec]):
                break                                  # okraj desky

            obsah = herni_plocha.vrat_obsah([radek, sloupec])
            if obsah is None:
                vysledek.append([radek, sloupec])      # prázdné pole
            else:
                if obsah.barva != figurka.barva:
                    vysledek.append([radek, sloupec])  # cizí figurku lze sebrat
                break                                  # dál už nejde

            # kůň (skok=True) a král udělají jen jeden krok,
            # dáma, věž a střelec pokračují dál
            if figurka.skok or not figurka.opakovat:
                break

        return vysledek

    def pohyby_pesaka(self, pesak, herni_plocha):
        # Pěšák má zvláštní pravidla pro pohyb a útok
        vysledek = []
        radek = pesak.pozice[0]
        sloupec = pesak.pozice[1]
        smer = pesak.vektory[0][0]           # -1 pro bílého, +1 pro černého

        # pohyb o 1 pole dopředu – jen na prázdné pole
        jedno_pole = [radek + smer, sloupec]
        if herni_plocha.je_na_desce(jedno_pole) and herni_plocha.vrat_obsah(jedno_pole) is None:
            vysledek.append(jedno_pole)

            # z počáteční pozice může jít o 2 pole (obě musí být prázdná)
            dve_pole = [radek + 2 * smer, sloupec]
            if pesak.pocet_tahu == 0 and herni_plocha.je_na_desce(dve_pole):
                if herni_plocha.vrat_obsah(dve_pole) is None:
                    vysledek.append(dve_pole)

        # útok diagonálně – jen když tam stojí cizí figurka
        for vektor in pesak.vektory_utoku:
            pole = [radek + vektor[0], sloupec + vektor[1]]
            obsah = herni_plocha.vrat_obsah(pole)
            if obsah is not None and obsah.barva != pesak.barva:
                vysledek.append(pole)

        return vysledek

    def napadena_pole(self, figurka, herni_plocha):
        # Vrátí pole, na která figurka útočí (používá se pro kontrolu šachu)
        vysledek = []
        if isinstance(figurka, Pesak):
            # pěšák útočí jen diagonálně
            for vektor in figurka.vektory_utoku:
                pole = [figurka.pozice[0] + vektor[0], figurka.pozice[1] + vektor[1]]
                if herni_plocha.je_na_desce(pole):
                    vysledek.append(pole)
        else:
            for vektor in figurka.vektory_utoku:
                vysledek = vysledek + self.pole_ve_smeru(figurka, vektor, herni_plocha)
        return vysledek

    def je_pole_napadeno(self, pole, barva_utocnika, herni_plocha):
        # Zjistí, zda na pole útočí některá figurka barvy barva_utocnika
        for figurka in herni_plocha.vsechny_figurky(barva_utocnika):
            if pole in self.napadena_pole(figurka, herni_plocha):
                return True
        return False

    def najdi_krale(self, barva, herni_plocha):
        for figurka in herni_plocha.vsechny_figurky(barva):
            if isinstance(figurka, Kral):
                return figurka
        return None

    def mozne_rosady(self, kral, herni_plocha):
        # Vrátí cílová pole krále pro rošádu (pokud je povolená)
        vysledek = []
        if kral.pocet_tahu != 0:
            return vysledek                      # král už táhl
        souper = 1 - kral.barva
        radek = kral.pozice[0]
        if self.je_pole_napadeno(kral.pozice, souper, herni_plocha):
            return vysledek                      # z šachu se rošáda dělat nesmí

        # krátká rošáda (věž na sloupci 7)
        vez = herni_plocha.vrat_obsah([radek, 7])
        if isinstance(vez, Vez) and vez.barva == kral.barva and vez.pocet_tahu == 0:
            if herni_plocha.vrat_obsah([radek, 5]) is None and herni_plocha.vrat_obsah([radek, 6]) is None:
                if not self.je_pole_napadeno([radek, 5], souper, herni_plocha):
                    if not self.je_pole_napadeno([radek, 6], souper, herni_plocha):
                        vysledek.append([radek, 6])

        # dlouhá rošáda (věž na sloupci 0)
        vez = herni_plocha.vrat_obsah([radek, 0])
        if isinstance(vez, Vez) and vez.barva == kral.barva and vez.pocet_tahu == 0:
            prazdne = True
            for sloupec in [1, 2, 3]:
                if herni_plocha.vrat_obsah([radek, sloupec]) is not None:
                    prazdne = False
            if prazdne:
                if not self.je_pole_napadeno([radek, 3], souper, herni_plocha):
                    if not self.je_pole_napadeno([radek, 2], souper, herni_plocha):
                        vysledek.append([radek, 2])

        return vysledek

    def necha_krale_v_sachu(self, figurka, cil, herni_plocha):
        # Zkusí tah "nanečisto" a zjistí, jestli by vlastní král zůstal v šachu.
        # Potom desku vrátí do původního stavu.
        start = figurka.pozice
        sebrana = herni_plocha.herni_deska[cil[0]][cil[1]]

        herni_plocha.herni_deska[start[0]][start[1]] = None
        herni_plocha.herni_deska[cil[0]][cil[1]] = figurka
        figurka.pozice = cil

        v_sachu = self.check_sach(figurka.barva, herni_plocha)

        # vrácení tahu zpět
        figurka.pozice = start
        herni_plocha.herni_deska[start[0]][start[1]] = figurka
        herni_plocha.herni_deska[cil[0]][cil[1]] = sebrana

        return v_sachu

    # ------------------------------------------------------------------
    # Hlavní metody
    # ------------------------------------------------------------------

    def simuluj_move(self, figurka, herni_plocha):
        # Vrátí seznam všech platných cílových souřadnic pro danou figurku
        if figurka is None or figurka.pozice is None:
            return []

        # 1) tahy podle pravidel pohybu figurky
        if isinstance(figurka, Pesak):
            kandidati = self.pohyby_pesaka(figurka, herni_plocha)
        else:
            kandidati = []
            for vektor in figurka.vektory:
                kandidati = kandidati + self.pole_ve_smeru(figurka, vektor, herni_plocha)
            if isinstance(figurka, Kral):
                kandidati = kandidati + self.mozne_rosady(figurka, herni_plocha)

        # 2) vyřadíme tahy, po kterých by vlastní král zůstal v šachu
        platne = []
        for cil in kandidati:
            if not self.necha_krale_v_sachu(figurka, cil, herni_plocha):
                platne.append(cil)
        return platne

    def over_tah(self, tah):
        # Ověří, zda je objekt Tah platný podle pravidel šachu
        self.tah = tah
        if tah is None or not tah.over_platnost():
            return False
        figurka = self.herni_plocha.vrat_obsah(tah.vychozi_pozice)
        if figurka is None or figurka is not tah.figurka:
            return False
        return tah.cilova_pozice in self.simuluj_move(figurka, self.herni_plocha)

    def ma_platny_tah(self, barva, herni_plocha):
        # Vrátí True, pokud má hráč dané barvy alespoň jeden platný tah
        for figurka in herni_plocha.vsechny_figurky(barva):
            if len(self.simuluj_move(figurka, herni_plocha)) > 0:
                return True
        return False

    def check_sach(self, barva, herni_plocha):
        # Vrátí True, pokud je král dané barvy v šachu
        kral = self.najdi_krale(barva, herni_plocha)
        if kral is None:
            return False
        return self.je_pole_napadeno(kral.pozice, 1 - barva, herni_plocha)

    def check_mat(self, barva, herni_plocha):
        # Mat = král je v šachu a hráč nemá žádný platný tah
        return self.check_sach(barva, herni_plocha) and not self.ma_platny_tah(barva, herni_plocha)

    def check_pat(self, barva, herni_plocha):
        # Pat = král není v šachu, ale hráč nemá žádný platný tah
        return not self.check_sach(barva, herni_plocha) and not self.ma_platny_tah(barva, herni_plocha)
