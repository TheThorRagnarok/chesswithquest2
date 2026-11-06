import os
import datetime

from model.uzivatel import Uzivatel
from model.hrac import Hrac
from model.herni_plocha import HerniPlocha
from model.tah import Tah
from model.revizor_tahu import RevizorTahu
from model.game_logger import GameLogger
from model.game_timer import GameTimer
from model.game_manager import GameManager
from model.chess_notation_writer import ChessNotationWriter
from model.kwest_manager import KwestManager
from model.vez import Vez
from model.kun import Kun
from model.strelec import Strelec
from model.dama import Dama
from model.kral import Kral
from model.pesak import Pesak

from view.view import SachovniceView

# složka, do které se ukládají záznamy partií
SLOZKA_PARTII = "partie"

# kolik kvestů dostane každý hráč na začátku partie
POCET_KVESTU = 4


class HraController:
    def __init__(self, root):
        # root (okno tkinteru) vytváří main.py, který spouští i mainloop
        self.root = root
        self.view = SachovniceView(root, self)

        self.vynuluj_hru()
        self.view.zobraz_hlavni_menu()

    def vynuluj_hru(self):
        # Nastaví všechny proměnné hry do výchozího stavu
        self.manager = None
        self.plocha = None
        self.casovac = None
        self.zapis = None                # ChessNotationWriter
        self.id_casovace = None          # číslo naplánovaného after()
        self.hra_bezi = False
        self.vybrana_figurka = None
        self.posledni_tah = None
        self.cislo_tahu = 1
        self.nazev_souboru = ""

    # ------------------------------------------------------------------
    # Menu a přepínání obrazovek
    # ------------------------------------------------------------------

    def ukonci_rozehranou(self, otazka):
        # Pokud se hraje, zeptá se hráče; vrátí True, když se smí pokračovat
        if self.hra_bezi:
            if not self.view.potvrd("Ukončit partii", otazka):
                return False
        self.zastav_casovac()
        self.vynuluj_hru()
        return True

    def hlavni_menu(self):
        if self.ukonci_rozehranou("Opravdu ukončit rozehranou partii a jít do menu?"):
            self.view.zobraz_hlavni_menu()

    def nova_hra(self):
        if self.ukonci_rozehranou("Opravdu ukončit rozehranou partii?"):
            self.view.zobraz_uvodni_obrazovku()

    def zobraz_pravidla(self):
        self.view.zobraz_okno_pravidla()

    def zobraz_kvesty(self):
        # Pošle do view seznam všech kvestů ze zásoby
        radky = []
        for kwest in KwestManager().kvesty:
            radky.append([kwest.nazev, kwest.popis, kwest.obtiznost])
        self.view.zobraz_okno_kvesty(radky)

    def zobraz_o_hre(self):
        self.view.zobraz_okno_o_hre()

    def zavri_aplikaci(self):
        self.zastav_casovac()
        self.root.destroy()

    # ------------------------------------------------------------------
    # Začátek hry
    # ------------------------------------------------------------------

    def zacni_hru(self, jmeno1, jmeno2, cas_limit_minuty):
        self.vynuluj_hru()

        # hráči
        uzivatel1 = Uzivatel(jmeno1, jmeno1, "", 1200)
        uzivatel2 = Uzivatel(jmeno2, jmeno2, "", 1200)
        hrac1 = Hrac(barva=0, uzivatel=uzivatel1)
        hrac2 = Hrac(barva=1, uzivatel=uzivatel2)

        # kvesty: každý hráč dostane vlastní náhodný výběr
        kwest_manager = KwestManager()
        hrac1.kvesty = kwest_manager.vyber_nahodne(POCET_KVESTU)
        hrac2.kvesty = kwest_manager.vyber_nahodne(POCET_KVESTU)

        # deska a figurky
        self.plocha = HerniPlocha()
        self.rozloz_figurky()

        # soubor se záznamem partie, např. partie/partie_novak_svoboda_2024-01-15_14-30-05.txt
        if not os.path.exists(SLOZKA_PARTII):
            os.makedirs(SLOZKA_PARTII)
        nyni = datetime.datetime.now()
        self.nazev_souboru = os.path.join(
            SLOZKA_PARTII,
            "partie_" + self.uprav_jmeno(jmeno1) + "_" + self.uprav_jmeno(jmeno2) + "_"
            + nyni.strftime("%Y-%m-%d_%H-%M-%S") + ".txt")
        logger = GameLogger(self.nazev_souboru)
        logger.vytvor_soubor(self.nazev_souboru)
        logger.uloz_text(f"Partie: {jmeno1} (bílý) vs. {jmeno2} (černý), "
                         f"{cas_limit_minuty} min, {nyni.strftime('%d.%m.%Y %H:%M')}")
        for hrac in [hrac1, hrac2]:
            nazvy = []
            for kwest in hrac.kvesty:
                nazvy.append(kwest.nazev)
            logger.uloz_text(f"Kvesty {hrac.uzivatel.jmeno}: " + ", ".join(nazvy))

        # časovač, revizor a manager hry
        self.casovac = GameTimer(cas_limit_minuty * 60)
        revizor = RevizorTahu(self.plocha, None)
        self.manager = GameManager(self.plocha, hrac1, hrac2, logger, revizor,
                                   self.casovac, kwest_manager)

        # zápis partie
        self.zapis = ChessNotationWriter("PGN")
        self.zapis.pridej_metadata("Event", "Školní šachy s kvesty")
        self.zapis.pridej_metadata("Date", nyni.strftime("%Y.%m.%d"))
        self.zapis.pridej_metadata("White", jmeno1)
        self.zapis.pridej_metadata("Black", jmeno2)
        self.zapis.pridej_metadata("TimeControl", str(cas_limit_minuty * 60))
        self.zapis.pridej_metadata("Result", "*")

        # přepnutí na herní obrazovku
        self.view.zobraz_herni_obrazovku(jmeno1, jmeno2)
        self.view.aktualizuj_desku(self.plocha.herni_deska)
        self.view.zobraz_vyhozene([], [])
        self.view.aktualizuj_cas(self.casovac.get_cas_bily(), self.casovac.get_cas_cerny())
        self.view.zobraz_aktivniho_hrace(jmeno1, 0)
        self.aktualizuj_kvesty_ve_view()
        self.view.zobraz_zpravu(f"Hra začala. Na tahu je {jmeno1} (bílý).")

        # spuštění hodin
        self.hra_bezi = True
        self.id_casovace = self.root.after(1000, self.tik_casovace)

    def uprav_jmeno(self, jmeno):
        # "Jan Novák" -> "jan_novák" (bez mezer a zvláštních znaků, aby šel použít v názvu souboru)
        vysledek = ""
        for znak in jmeno.lower():
            if znak.isalnum():
                vysledek = vysledek + znak
            else:
                vysledek = vysledek + "_"
        return vysledek

    def rozloz_figurky(self):
        # Rozmístí figurky na standardní počáteční pozice
        poradi = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]   # třídy figurek
        for sloupec in range(8):
            # černé figurky (barva 1) nahoře
            self.plocha.poloz_figurku(poradi[sloupec](1), [0, sloupec])
            self.plocha.poloz_figurku(Pesak(1), [1, sloupec])
            # bílé figurky (barva 0) dole
            self.plocha.poloz_figurku(Pesak(0), [6, sloupec])
            self.plocha.poloz_figurku(poradi[sloupec](0), [7, sloupec])

    # ------------------------------------------------------------------
    # Tahy
    # ------------------------------------------------------------------

    def kliknuti_na_pole(self, radek, sloupec):
        if not self.hra_bezi:
            return

        aktivni = self.manager.aktivni_hrac
        pole = [radek, sloupec]
        obsah = self.plocha.vrat_obsah(pole)

        # Kliknutí na vlastní figurku = výběr (nebo změna výběru)
        if obsah is not None and obsah.barva == aktivni:
            if obsah is self.vybrana_figurka:
                # druhé kliknutí na stejnou figurku výběr zruší
                self.zrus_vyber()
                return
            self.vyber_figurku(obsah)
            return

        # Žádná figurka není vybraná a hráč klikl na prázdné pole / soupeře
        if self.vybrana_figurka is None:
            if obsah is None:
                self.view.zobraz_zpravu("Vyber svou figurku.")
            else:
                self.view.zobraz_zpravu("To není tvoje figurka.", True)
            return

        # Druhé kliknutí – pokus o tah
        vychozi = [self.vybrana_figurka.pozice[0], self.vybrana_figurka.pozice[1]]
        if not self.proved_tah(vychozi, pole):
            self.zrus_vyber()
            self.view.zobraz_zpravu("Neplatný tah", True)
            return

        # Tah proběhl: kvesty, překreslení, přepnutí hráče, kontrola šachu/matu
        hrac = self.manager.get_aktivni_hrac()
        nove_kvesty = self.manager.zpracuj_kvesty(self.posledni_tah)

        self.zrus_vyber()
        self.view.oznac_posledni_tah(vychozi, pole)
        self.view.zobraz_vyhozene(self.plocha.vyhozene_figurky_b,
                                  self.plocha.vyhozene_figurky_c)
        self.aktualizuj_kvesty_ve_view()

        if hrac.splnil_vsechny_kvesty():
            self.view.aktualizuj_desku(self.plocha.herni_deska)
            self.konec_hry(hrac, "splnil všechny kvesty")
            return

        self.prepni_hrace()
        stav = self.zkontroluj_stav_hry()
        if stav == "konec":
            return

        # zpráva pro hráče
        na_tahu = self.manager.get_aktivni_hrac().uzivatel.jmeno
        if len(nove_kvesty) > 0:
            nazvy = []
            for kwest in nove_kvesty:
                nazvy.append(kwest.nazev)
            text = f"✓ {hrac.uzivatel.jmeno} splnil kvest: " + ", ".join(nazvy) + "."
            if stav == "sach":
                text = text + " A je to šach!"
            self.view.zobraz_zpravu(text)
        elif stav == "sach":
            self.view.zobraz_zpravu(f"Šach! {na_tahu} musí krále ochránit.", True)
        else:
            self.view.zobraz_zpravu(f"Na tahu je {na_tahu}.")

    def vyber_figurku(self, figurka):
        self.vybrana_figurka = figurka
        mozne = self.manager.zacni_tah(figurka)
        self.view.oznac_pole(figurka.pozice)
        self.view.zvyrazni_pole(mozne)
        text = f"Vybráno: {figurka.nazev} {self.souradnice_na_notaci(figurka.pozice)}"
        if len(mozne) == 0:
            text = text + ". Tahle figurka teď nemůže táhnout."
        self.view.zobraz_zpravu(text)

    def zrus_vyber(self):
        self.vybrana_figurka = None
        self.manager.zrus_tah()
        self.view.zrus_zvyrazneni()

    def proved_tah(self, vychozi, cilova):
        # Vytvoří tah, nechá ho ověřit a provede ho. Vrátí True/False.
        figurka = self.plocha.vrat_obsah(vychozi)
        if figurka is None:
            return False
        tah = Tah(vychozi, cilova, figurka, "normalni")

        # GameManager ověří tah přes RevizorTahu, provede ho a uloží do GameLoggeru
        self.manager.mozne_tahy(tah)
        if not self.manager.proved_tah():
            return False

        # zápis do notace
        self.zapis.pridej_tah(tah, self.cislo_tahu, figurka.barva)
        if figurka.barva == 1:
            self.cislo_tahu = self.cislo_tahu + 1   # po tahu černého začíná další číslo tahu
        self.posledni_tah = tah
        return True

    def prepni_hrace(self):
        self.manager.prepni_hrace()
        hrac = self.manager.get_aktivni_hrac()
        self.view.zobraz_aktivniho_hrace(hrac.uzivatel.jmeno, hrac.barva)

    def zkontroluj_stav_hry(self):
        # Kontrola pro hráče, který je právě na tahu.
        # Vrátí "konec" (mat/pat), "sach" nebo "hra".
        revizor = self.manager.revizor_tahu
        barva = self.manager.aktivni_hrac

        if revizor.check_sach(barva, self.plocha):
            kral = revizor.najdi_krale(barva, self.plocha)
            self.view.oznac_sach(kral.pozice)
        else:
            self.view.oznac_sach(None)
        self.view.aktualizuj_desku(self.plocha.herni_deska)

        if revizor.check_mat(barva, self.plocha):
            self.zapis.pridej_znacku("#")
            self.konec_hry(self.manager.get_souper(), "dal soupeři mat")
            return "konec"
        if revizor.check_pat(barva, self.plocha):
            self.konec_hry(None, "pat")
            return "konec"
        if revizor.check_sach(barva, self.plocha):
            self.zapis.pridej_znacku("+")
            return "sach"
        return "hra"

    def aktualizuj_kvesty_ve_view(self):
        # Pošle do view stav kvestů obou hráčů
        for hrac in self.manager.hraci:
            self.view.aktualizuj_kvesty(hrac.barva, self.radky_kvestu(hrac))

    def radky_kvestu(self, hrac):
        # Převede kvesty hráče na jednoduché řádky [popis, postup, splněno] pro view
        radky = []
        for kwest in hrac.kvesty:
            radky.append([kwest.popis, kwest.postup_text(hrac.statistika), kwest.splneny])
        return radky

    # ------------------------------------------------------------------
    # Časovač
    # ------------------------------------------------------------------

    def tik_casovace(self):
        if not self.hra_bezi:
            return
        zbyva = self.casovac.odecti_sekundu()
        self.view.aktualizuj_cas(self.casovac.get_cas_bily(), self.casovac.get_cas_cerny())

        if zbyva <= 0:
            self.id_casovace = None
            # čas došel hráči na tahu -> vyhrává soupeř
            self.konec_hry(self.manager.get_souper(), "soupeři došel čas")
            return

        self.id_casovace = self.root.after(1000, self.tik_casovace)

    def zastav_casovac(self):
        if self.id_casovace is not None:
            self.root.after_cancel(self.id_casovace)
            self.id_casovace = None

    # ------------------------------------------------------------------
    # Konec hry
    # ------------------------------------------------------------------

    def konec_hry(self, vitez, duvod):
        # vitez = objekt Hrac, nebo None při remíze; duvod = text (mat, pat, ...)
        if not self.hra_bezi:
            return                      # konec už byl zpracovaný
        self.hra_bezi = False
        self.zastav_casovac()

        if vitez is None:
            vysledek = "1/2-1/2"
            nadpis = "Remíza"
            podnadpis = f"Partie skončila: {duvod}."
        else:
            if vitez.barva == 0:
                vysledek = "1-0"
                barva_text = "bílý"
            else:
                vysledek = "0-1"
                barva_text = "černý"
            nadpis = f"Vyhrál {vitez.uzivatel.jmeno}"
            podnadpis = f"{barva_text.capitalize()} vyhrává: {duvod}."

        self.zapis.nastav_vysledek(vysledek)
        pgn = self.zapis.get_cely_zapis()

        # souhrn kvestů obou hráčů
        radky = []
        souhrn = ""
        for hrac in self.manager.hraci:
            radky.append(self.radky_kvestu(hrac))
            souhrn = souhrn + f"Kvesty {hrac.uzivatel.jmeno}: "
            souhrn = souhrn + f"{hrac.pocet_splnenych_kvestu()}/{len(hrac.kvesty)} splněno\n"

        # uložení celé partie do souboru přes GameLogger
        self.manager.uloz_log("\n" + nadpis + ". " + podnadpis + "\n" + souhrn + "\n" + pgn)

        podnadpis = podnadpis + "\nPartie je uložená v souboru " + self.nazev_souboru
        self.view.zobraz_konec(nadpis, podnadpis, pgn, radky)

    def vzdani_se(self):
        if not self.hra_bezi:
            return
        hrac = self.manager.get_aktivni_hrac()
        if not self.view.potvrd("Vzdát se", f"{hrac.uzivatel.jmeno}, opravdu se chceš vzdát?"):
            return
        # Během otevřeného dialogu mohl dojít čas a hra skončit
        if not self.hra_bezi:
            return
        self.konec_hry(self.manager.get_souper(), "soupeř se vzdal")

    # ------------------------------------------------------------------
    # Převody souřadnic
    # ------------------------------------------------------------------

    def notace_na_souradnice(self, notace):
        # "e2" -> [6, 4]
        pismena = "abcdefgh"
        sloupec = pismena.index(notace[0].lower())
        radek = 8 - int(notace[1])
        return [radek, sloupec]

    def souradnice_na_notaci(self, souradnice):
        # [6, 4] -> "e2"
        pismena = "abcdefgh"
        return pismena[souradnice[1]] + str(8 - souradnice[0])
