import tkinter as tk
import tkinter.font as tkfont
from tkinter import messagebox
from tkinter import scrolledtext

from view.tlacitko import Tlacitko

# ----------------------------------------------------------------------
# Rozměry
# ----------------------------------------------------------------------
VELIKOST_POLE = 64           # velikost jednoho pole šachovnice v pixelech
OKRAJ = 24                   # okraj kolem desky pro popisky a–h a 1–8
VELIKOST_DESKY = 8 * VELIKOST_POLE + 2 * OKRAJ
SIRKA_PANELU = 330           # pravý panel s kartami hráčů
MEZERA = 20                  # základní mezera mezi bloky
SIRKA_OKNA = VELIKOST_DESKY + SIRKA_PANELU + 3 * MEZERA
VYSKA_OKNA = VELIKOST_DESKY + 2 * MEZERA

# ----------------------------------------------------------------------
# Barvy (jedna akcentová barva – zelená, zbytek jsou odstíny šedé)
# Kontrast textu je ověřený (aspoň 4.5 : 1 pro běžný text).
# ----------------------------------------------------------------------
BARVA_POZADI = "#3C3C3C"          # tmavě šedé pozadí okna
BARVA_KARTA = "#474747"           # karty a panely o odstín světlejší
BARVA_POLE_TEXT = "#2F2F2F"       # textová pole (vstupy, zápis partie)
BARVA_RAMECEK = "#5A5A5A"
BARVA_TEXT = "#EEEEEE"            # hlavní text
BARVA_TEXT_2 = "#B8B8B8"          # vedlejší text (popisky, neaktivní hodiny)
BARVA_AKCENT = "#4CAF50"          # zelená: aktivní hráč, možné tahy
BARVA_HOTOVO = "#7BD67F"          # splněný kvest
BARVA_CHYBA = "#FFB4AB"           # šach, neplatný tah, dochází čas

# šachovnice
BARVA_SVETLA = "#F0D9B5"
BARVA_TMAVA = "#B58863"
BARVA_VYBRANE = "#F6F669"         # označená figurka
BARVA_POSLEDNI_SVETLA = "#CDD26A" # poslední tah na světlém poli
BARVA_POSLEDNI_TMAVA = "#AAA23A"  # poslední tah na tmavém poli
BARVA_SACH = "#E5534B"            # král v šachu

# tlačítka: [pozadí, pozadí při najetí, pozadí při stisku, barva textu]
STYLY_TLACITEK = {
    "hlavni": ["#2E7D32", "#388E3C", "#1B5E20", "#FFFFFF"],
    "vedlejsi": ["#505050", "#5C5C5C", "#444444", BARVA_TEXT],
    "nebezpeci": ["#505050", "#5C5C5C", "#444444", BARVA_CHYBA],
}

# Unicode symboly figurek: [bílá, černá]
SYMBOLY = {
    "Král": ["♔", "♚"],
    "Dáma": ["♕", "♛"],
    "Věž": ["♖", "♜"],
    "Střelec": ["♗", "♝"],
    "Kůň": ["♘", "♞"],
    "Pěšák": ["♙", "♟"],
}

PISMO_FIGUREK = ("Segoe UI Symbol", 36)

TEXT_PRAVIDEL = """CÍL HRY
Vyhrát můžeš dvěma způsoby:
  • dáš soupeři mat, nebo
  • jako první splníš všechny své 4 kvesty.
Pat je remíza. Když ti dojde čas, prohráváš.

JAK TÁHNOUT
1. Klikni na svou figurku – zelené tečky ukážou, kam může táhnout
   (zelený rámeček = můžeš sebrat soupeřovu figurku).
2. Klikni na cílové pole.
Druhým kliknutím na stejnou figurku výběr zrušíš.

SPECIÁLNÍ TAHY
  • Rošáda: klikni na krále a pak o dvě pole do strany.
    Král i věž ještě nesmí táhnout a král nesmí být v šachu.
  • Proměna: pěšák na poslední řadě se změní v dámu.
  • Pěšák může z výchozí pozice jít o dvě pole.

KVESTY
Na začátku partie dostane každý hráč 4 náhodné kvesty ze zásoby.
Postup vidíš na své kartě vpravo (např. 1/3). Splněný kvest se odškrtne.

HODINY
Čas běží hráči, který je na tahu. Poslední vteřiny se zbarví červeně."""


class SachovniceView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.root.title("Šachy s kvesty")
        self.root.configure(bg=BARVA_POZADI)
        self.root.geometry(f"{SIRKA_OKNA}x{VYSKA_OKNA}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.controller.zavri_aplikaci)

        # Systémové písmo (na Macu San Francisco, na Windows Segoe UI)
        # a písmo se stejně širokými číslicemi pro hodiny.
        self.pismo = tkfont.nametofont("TkDefaultFont").actual("family")
        self.pismo_cisla = tkfont.nametofont("TkFixedFont").actual("family")

        # stav herní obrazovky
        self.herni_deska = None
        self.vybrane_pole = None          # [radek, sloupec] označené figurky
        self.zvyraznena_pole = []         # seznam polí možných tahů
        self.posledni_tah = []            # [odkud, kam] posledního tahu
        self.pole_sach = None             # pole krále v šachu
        self.canvas = None
        self.aktivni_barva = 0
        self.jmena = ["", ""]             # [jméno bílého, jméno černého]

        self.vytvor_menu_listu()

    # ------------------------------------------------------------------
    # Pomocné metody
    # ------------------------------------------------------------------

    def font(self, velikost, styl):
        # styl = "normal" nebo "bold"
        return (self.pismo, velikost, styl)

    def vycisti_okno(self):
        # Smaže obsah okna před přepnutím obrazovky.
        # Horní lištu menu a otevřená okna (pravidla, kvesty) necháme být.
        for prvek in self.root.winfo_children():
            if isinstance(prvek, tk.Menu) or isinstance(prvek, tk.Toplevel):
                continue
            prvek.destroy()
        self.root.unbind("<Return>")
        self.canvas = None

    def symbol_figurky(self, figurka):
        return SYMBOLY[figurka.nazev][figurka.barva]

    def potvrd(self, titulek, otazka):
        # Zobrazí dialog Ano/Ne a vrátí True/False
        return messagebox.askyesno(titulek, otazka)

    def tlacitko(self, rodic, text, prikaz, styl, hodnota=None):
        # Vytvoří tlačítko v jednom ze stylů: "hlavni", "vedlejsi", "nebezpeci"
        return Tlacitko(rodic, text, prikaz, STYLY_TLACITEK[styl],
                        self.font(13, "bold"), hodnota)

    def popisek(self, rodic, text, velikost, styl, barva):
        # Zkratka pro tk.Label na pozadí okna
        return tk.Label(rodic, text=text, font=self.font(velikost, styl),
                        bg=rodic.cget("bg"), fg=barva, justify="left")

    def vstupni_pole(self, rodic, vychozi_text):
        pole = tk.Entry(rodic, font=self.font(13, "normal"), width=24,
                        bg=BARVA_POLE_TEXT, fg=BARVA_TEXT, insertbackground=BARVA_TEXT,
                        relief="flat", highlightthickness=1,
                        highlightbackground=BARVA_RAMECEK, highlightcolor=BARVA_AKCENT)
        pole.insert(0, vychozi_text)
        return pole

    # ------------------------------------------------------------------
    # Horní lišta menu
    # ------------------------------------------------------------------

    def vytvor_menu_listu(self):
        lista = tk.Menu(self.root)

        menu_hra = tk.Menu(lista, tearoff=0)
        menu_hra.add_command(label="Hlavní menu", command=self.controller.hlavni_menu)
        menu_hra.add_command(label="Nová hra…", command=self.controller.nova_hra)
        menu_hra.add_command(label="Vzdát se", command=self.controller.vzdani_se)
        menu_hra.add_separator()
        menu_hra.add_command(label="Ukončit", command=self.controller.zavri_aplikaci)
        lista.add_cascade(label="Hra", menu=menu_hra)

        menu_napoveda = tk.Menu(lista, tearoff=0)
        menu_napoveda.add_command(label="Pravidla", command=self.controller.zobraz_pravidla)
        menu_napoveda.add_command(label="Seznam kvestů", command=self.controller.zobraz_kvesty)
        menu_napoveda.add_separator()
        menu_napoveda.add_command(label="O hře", command=self.controller.zobraz_o_hre)
        lista.add_cascade(label="Nápověda", menu=menu_napoveda)

        self.root.config(menu=lista)

    # ------------------------------------------------------------------
    # Hlavní menu
    # ------------------------------------------------------------------

    def zobraz_hlavni_menu(self):
        self.vycisti_okno()

        ramec = tk.Frame(self.root, bg=BARVA_POZADI)
        ramec.place(relx=0.5, rely=0.5, anchor="center")   # doprostřed okna

        tk.Label(ramec, text="♚", font=("Segoe UI Symbol", 64),
                 bg=BARVA_POZADI, fg=BARVA_TEXT).pack()
        self.popisek(ramec, "Šachy s kvesty", 32, "bold", BARVA_TEXT).pack()
        self.popisek(ramec, "Dej mat, nebo splň své 4 kvesty dřív než soupeř.",
                     13, "normal", BARVA_TEXT_2).pack(pady=(6, 28))

        polozky = [
            ["Nová hra", self.controller.nova_hra, "hlavni"],
            ["Seznam kvestů", self.controller.zobraz_kvesty, "vedlejsi"],
            ["Pravidla", self.controller.zobraz_pravidla, "vedlejsi"],
            ["Ukončit", self.controller.zavri_aplikaci, "vedlejsi"],
        ]
        for polozka in polozky:
            tlacitko = self.tlacitko(ramec, polozka[0], polozka[1], polozka[2])
            tlacitko.config(width=22)
            tlacitko.pack(pady=5)

        self.popisek(ramec, "Školní projekt ChessWithQuests", 10, "normal",
                     BARVA_TEXT_2).pack(pady=(28, 0))

    # ------------------------------------------------------------------
    # Úvodní obrazovka – nastavení nové hry
    # ------------------------------------------------------------------

    def zobraz_uvodni_obrazovku(self):
        self.vycisti_okno()

        ramec = tk.Frame(self.root, bg=BARVA_KARTA, padx=36, pady=28)
        ramec.place(relx=0.5, rely=0.5, anchor="center")

        self.popisek(ramec, "Nová hra", 24, "bold", BARVA_TEXT).pack(anchor="w")
        self.popisek(ramec, "Zadej jména hráčů a délku partie.", 12, "normal",
                     BARVA_TEXT_2).pack(anchor="w", pady=(2, 20))

        self.popisek(ramec, "♔  Bílý hráč", 12, "bold", BARVA_TEXT_2).pack(anchor="w")
        self.pole_jmeno1 = self.vstupni_pole(ramec, "Hráč 1")
        self.pole_jmeno1.pack(anchor="w", fill="x", ipady=6, pady=(4, 14))

        self.popisek(ramec, "♚  Černý hráč", 12, "bold", BARVA_TEXT_2).pack(anchor="w")
        self.pole_jmeno2 = self.vstupni_pole(ramec, "Hráč 2")
        self.pole_jmeno2.pack(anchor="w", fill="x", ipady=6, pady=(4, 14))

        # výběr délky hry jako "segmentový přepínač" (tři tlačítka vedle sebe)
        self.popisek(ramec, "Délka partie", 12, "bold", BARVA_TEXT_2).pack(anchor="w")
        ramec_casu = tk.Frame(ramec, bg=BARVA_KARTA)
        ramec_casu.pack(anchor="w", pady=(4, 14))
        self.delka_hry = 5
        self.tlacitka_casu = []
        for minuty in [2, 5, 10]:
            tlacitko = self.tlacitko(ramec_casu, f"{minuty} min", self.vyber_delku,
                                     "vedlejsi", minuty)
            tlacitko.config(width=6)
            tlacitko.pack(side="left", padx=(0, 6))
            self.tlacitka_casu.append(tlacitko)
        self.vyber_delku(5)

        self.popisek(ramec, "Každý hráč dostane 4 náhodné kvesty.\nKdo je splní všechny, vyhrává.",
                     11, "normal", BARVA_TEXT_2).pack(anchor="w")

        self.chyba_uvod = self.popisek(ramec, "", 11, "normal", BARVA_CHYBA)
        self.chyba_uvod.pack(anchor="w", pady=(6, 6))

        tlacitka = tk.Frame(ramec, bg=BARVA_KARTA)
        tlacitka.pack(fill="x")
        self.tlacitko(tlacitka, "Spustit hru", self.stisk_spustit, "hlavni").pack(side="right")
        self.tlacitko(tlacitka, "Zpět", self.controller.hlavni_menu,
                      "vedlejsi").pack(side="right", padx=(0, 8))

        self.root.bind("<Return>", self.klavesa_enter)   # Enter = Spustit hru
        self.pole_jmeno1.focus_set()

    def vyber_delku(self, minuty):
        # Zvýrazní vybranou délku hry, ostatní tlačítka vrátí do šedé
        self.delka_hry = minuty
        moznosti = [2, 5, 10]
        for i in range(3):
            if moznosti[i] == minuty:
                self.tlacitka_casu[i].nastav_barvy(STYLY_TLACITEK["hlavni"])
            else:
                self.tlacitka_casu[i].nastav_barvy(STYLY_TLACITEK["vedlejsi"])

    def klavesa_enter(self, udalost):
        self.stisk_spustit()

    def stisk_spustit(self):
        jmeno1 = self.pole_jmeno1.get().strip()
        jmeno2 = self.pole_jmeno2.get().strip()
        if jmeno1 == "" or jmeno2 == "":
            self.chyba_uvod.config(text="Zadej jména obou hráčů.")
            return
        self.controller.zacni_hru(jmeno1, jmeno2, self.delka_hry)

    # ------------------------------------------------------------------
    # Herní obrazovka
    # ------------------------------------------------------------------

    def zobraz_herni_obrazovku(self, jmeno_bileho, jmeno_cerneho):
        self.vycisti_okno()
        self.vybrane_pole = None
        self.zvyraznena_pole = []
        self.posledni_tah = []
        self.pole_sach = None
        self.jmena = [jmeno_bileho, jmeno_cerneho]

        hlavni = tk.Frame(self.root, bg=BARVA_POZADI)
        hlavni.place(relx=0.5, rely=0.5, anchor="center")

        # --- šachovnice vlevo ---
        self.canvas = tk.Canvas(hlavni, width=VELIKOST_DESKY, height=VELIKOST_DESKY,
                                bg=BARVA_POZADI, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self.klik_na_canvas)

        # --- panel vpravo: karta černého nahoře, bílého dole (jako na desce) ---
        panel = tk.Frame(hlavni, bg=BARVA_POZADI, width=SIRKA_PANELU, height=VELIKOST_DESKY)
        panel.grid(row=0, column=1, padx=(MEZERA, 0))
        panel.pack_propagate(False)       # panel má pevnou velikost

        # Seznamy s indexem podle barvy: [0] = bílý, [1] = černý
        self.karty = [None, None]
        self.label_cas = [None, None]
        self.label_sebrane = [None, None]
        self.label_kvesty = [None, None]
        self.radky_kvestu = [[], []]

        self.vytvor_kartu_hrace(panel, 1, jmeno_cerneho).pack(side="top", fill="x")
        self.vytvor_kartu_hrace(panel, 0, jmeno_bileho).pack(side="bottom", fill="x")

        # --- prostředek panelu: zpráva a tlačítka ---
        stred = tk.Frame(panel, bg=BARVA_POZADI)
        stred.pack(fill="both", expand=True)
        vnitrek = tk.Frame(stred, bg=BARVA_POZADI)
        vnitrek.place(relx=0, rely=0.5, anchor="w", relwidth=1)

        self.label_zprava = tk.Label(vnitrek, text="", font=self.font(13, "normal"),
                                     bg=BARVA_POZADI, fg=BARVA_TEXT, wraplength=SIRKA_PANELU,
                                     justify="left", anchor="w")
        self.label_zprava.pack(fill="x", pady=(0, 10))

        tlacitka = tk.Frame(vnitrek, bg=BARVA_POZADI)
        tlacitka.pack(fill="x")
        self.tlacitko(tlacitka, "Vzdát se", self.controller.vzdani_se,
                      "nebezpeci").pack(side="left")
        self.tlacitko(tlacitka, "Nová hra", self.controller.nova_hra,
                      "vedlejsi").pack(side="left", padx=(8, 0))

    def vytvor_kartu_hrace(self, rodic, barva, jmeno):
        # Karta jednoho hráče: jméno, hodiny, sebrané figurky a kvesty
        karta = tk.Frame(rodic, bg=BARVA_KARTA, padx=14, pady=12,
                         highlightthickness=2, highlightbackground=BARVA_KARTA)
        self.karty[barva] = karta

        hlavicka = tk.Frame(karta, bg=BARVA_KARTA)
        hlavicka.pack(fill="x")
        symbol = SYMBOLY["Král"][barva]
        tk.Label(hlavicka, text=symbol + "  " + jmeno, font=self.font(14, "bold"),
                 bg=BARVA_KARTA, fg=BARVA_TEXT).pack(side="left")
        self.label_cas[barva] = tk.Label(hlavicka, text="", font=(self.pismo_cisla, 20, "bold"),
                                         bg=BARVA_KARTA, fg=BARVA_TEXT_2)
        self.label_cas[barva].pack(side="right")

        self.label_sebrane[barva] = tk.Label(karta, text="", bg=BARVA_KARTA, fg=BARVA_TEXT,
                                             anchor="w")
        self.label_sebrane[barva].pack(fill="x", pady=(4, 6))

        self.label_kvesty[barva] = tk.Label(karta, text="KVESTY", font=self.font(10, "bold"),
                                            bg=BARVA_KARTA, fg=BARVA_TEXT_2, anchor="w")
        self.label_kvesty[barva].pack(fill="x")

        for i in range(4):
            radek = tk.Frame(karta, bg=BARVA_KARTA)
            radek.pack(fill="x", pady=1)
            # postup balíme jako první, aby měl vždy místo a dlouhý text ho nepřekryl
            postup = tk.Label(radek, text="", font=(self.pismo_cisla, 11, "normal"),
                              bg=BARVA_KARTA, fg=BARVA_TEXT_2)
            postup.pack(side="right")
            text = tk.Label(radek, text="", font=self.font(11, "normal"),
                            bg=BARVA_KARTA, fg=BARVA_TEXT, anchor="w")
            text.pack(side="left", fill="x", expand=True)
            self.radky_kvestu[barva].append([text, postup])

        return karta

    def klik_na_canvas(self, udalost):
        # Převede souřadnice myši na řádek a sloupec šachovnice
        sloupec = (udalost.x - OKRAJ) // VELIKOST_POLE
        radek = (udalost.y - OKRAJ) // VELIKOST_POLE
        if 0 <= radek < 8 and 0 <= sloupec < 8:
            self.controller.kliknuti_na_pole(radek, sloupec)

    def aktualizuj_desku(self, herni_deska):
        # Překreslí celou šachovnici podle aktuálního stavu
        self.herni_deska = herni_deska
        self.prekresli()

    def prekresli(self):
        if self.canvas is None or self.herni_deska is None:
            return
        self.canvas.delete("all")

        pismena = "abcdefgh"
        for radek in range(8):
            for sloupec in range(8):
                x = OKRAJ + sloupec * VELIKOST_POLE
                y = OKRAJ + radek * VELIKOST_POLE
                pole = [radek, sloupec]
                svetle = (radek + sloupec) % 2 == 0

                # barva pole: základní -> poslední tah -> šach -> vybraná figurka
                if svetle:
                    barva = BARVA_SVETLA
                else:
                    barva = BARVA_TMAVA
                if pole in self.posledni_tah:
                    if svetle:
                        barva = BARVA_POSLEDNI_SVETLA
                    else:
                        barva = BARVA_POSLEDNI_TMAVA
                if pole == self.pole_sach:
                    barva = BARVA_SACH
                if pole == self.vybrane_pole:
                    barva = BARVA_VYBRANE
                self.canvas.create_rectangle(x, y, x + VELIKOST_POLE, y + VELIKOST_POLE,
                                             fill=barva, outline=barva)

                # figurka
                figurka = self.herni_deska[radek][sloupec]
                stred_x = x + VELIKOST_POLE // 2
                stred_y = y + VELIKOST_POLE // 2
                if figurka is not None:
                    self.canvas.create_text(stred_x, stred_y + 2, text=self.symbol_figurky(figurka),
                                            font=PISMO_FIGUREK, fill="black")

                # zvýraznění možného tahu
                if pole in self.zvyraznena_pole:
                    if figurka is None:
                        r = 9    # prázdné pole -> zelená tečka
                        self.canvas.create_oval(stred_x - r, stred_y - r, stred_x + r, stred_y + r,
                                                fill=BARVA_AKCENT, outline=BARVA_AKCENT)
                    else:
                        # figurku lze sebrat -> zelený rámeček
                        self.canvas.create_rectangle(x + 2, y + 2,
                                                     x + VELIKOST_POLE - 2, y + VELIKOST_POLE - 2,
                                                     outline=BARVA_AKCENT, width=4)

        # popisky sloupců (a–h) a řádků (8–1)
        konec = OKRAJ + 8 * VELIKOST_POLE
        for i in range(8):
            stred = OKRAJ + i * VELIKOST_POLE + VELIKOST_POLE // 2
            for y in [OKRAJ // 2, konec + OKRAJ // 2]:
                self.canvas.create_text(stred, y, text=pismena[i],
                                        font=self.font(11, "normal"), fill=BARVA_TEXT_2)
            for x in [OKRAJ // 2, konec + OKRAJ // 2]:
                self.canvas.create_text(x, stred, text=str(8 - i),
                                        font=self.font(11, "normal"), fill=BARVA_TEXT_2)

    def oznac_pole(self, souradnice):
        # Zvýrazní pole s vybranou figurkou
        self.vybrane_pole = souradnice
        self.prekresli()

    def zvyrazni_pole(self, souradnice_seznam):
        # Zvýrazní pole, kam může vybraná figurka táhnout
        self.zvyraznena_pole = souradnice_seznam
        self.prekresli()

    def zrus_zvyrazneni(self):
        self.vybrane_pole = None
        self.zvyraznena_pole = []
        self.prekresli()

    def oznac_posledni_tah(self, odkud, kam):
        self.posledni_tah = [odkud, kam]

    def oznac_sach(self, pole_krale):
        # pole_krale = [radek, sloupec] krále v šachu, nebo None
        self.pole_sach = pole_krale

    def zobraz_aktivniho_hrace(self, jmeno, barva):
        # Kartu hráče na tahu orámuje zeleně a rozsvítí jeho hodiny
        self.aktivni_barva = barva
        for b in [0, 1]:
            if b == barva:
                self.karty[b].config(highlightbackground=BARVA_AKCENT)
            else:
                self.karty[b].config(highlightbackground=BARVA_KARTA)
        self.obarvi_hodiny()

    def aktualizuj_cas(self, cas_bile, cas_cerne):
        # cas_bile a cas_cerne jsou texty ve formátu "MM:SS"
        self.label_cas[0].config(text=cas_bile)
        self.label_cas[1].config(text=cas_cerne)
        self.obarvi_hodiny()

    def obarvi_hodiny(self):
        for b in [0, 1]:
            text = self.label_cas[b].cget("text")
            if text != "" and text <= "00:20":
                barva = BARVA_CHYBA            # posledních 20 sekund
            elif b == self.aktivni_barva:
                barva = BARVA_TEXT
            else:
                barva = BARVA_TEXT_2
            self.label_cas[b].config(fg=barva)

    def zobraz_zpravu(self, zprava, dulezita=False):
        # dulezita = True -> červeně (šach, neplatný tah)
        if dulezita:
            self.label_zprava.config(text=zprava, fg=BARVA_CHYBA)
        else:
            self.label_zprava.config(text=zprava, fg=BARVA_TEXT)

    def zobraz_vyhozene(self, figurky_b, figurky_c):
        # figurky_b = vyhozené bílé figurky (sebral je černý),
        # figurky_c = vyhozené černé figurky (sebral je bílý)
        sebrane = [figurky_c, figurky_b]     # [co sebral bílý, co sebral černý]
        for b in [0, 1]:
            text = ""
            for figurka in sebrane[b]:
                text = text + SYMBOLY[figurka.nazev][1]
            if text == "":
                self.label_sebrane[b].config(text="Zatím nic nesebral",
                                             font=self.font(11, "normal"), fg=BARVA_TEXT_2)
            else:
                self.label_sebrane[b].config(text=text, font=("Segoe UI Symbol", 16),
                                             fg=BARVA_TEXT)

    def aktualizuj_kvesty(self, barva, radky):
        # radky = seznam [popis, postup "1/3", splneno True/False] pro každý kvest
        splneno = 0
        for i in range(len(radky)):
            popis = radky[i][0]
            postup = radky[i][1]
            hotovo = radky[i][2]
            label_text = self.radky_kvestu[barva][i][0]
            label_postup = self.radky_kvestu[barva][i][1]
            if hotovo:
                splneno = splneno + 1
                label_text.config(text="✓  " + popis, fg=BARVA_HOTOVO)
                label_postup.config(text=postup, fg=BARVA_HOTOVO)
            else:
                label_text.config(text="○  " + popis, fg=BARVA_TEXT)
                label_postup.config(text=postup, fg=BARVA_TEXT_2)
        self.label_kvesty[barva].config(text=f"KVESTY  {splneno}/{len(radky)}")

    # ------------------------------------------------------------------
    # Koncová obrazovka
    # ------------------------------------------------------------------

    def zobraz_konec(self, nadpis, podnadpis, pgn_zapis, radky_kvestu):
        # radky_kvestu = [kvesty bílého, kvesty černého], řádky jako u aktualizuj_kvesty
        self.vycisti_okno()

        ramec = tk.Frame(self.root, bg=BARVA_POZADI)
        ramec.place(relx=0.5, rely=0.5, anchor="center")

        self.popisek(ramec, nadpis, 26, "bold", BARVA_TEXT).pack()
        podnadpis_label = self.popisek(ramec, podnadpis, 13, "normal", BARVA_TEXT_2)
        podnadpis_label.config(justify="center")
        podnadpis_label.pack(pady=(4, 14))

        # souhrn kvestů obou hráčů vedle sebe
        souhrn = tk.Frame(ramec, bg=BARVA_POZADI)
        souhrn.pack(fill="x")
        for b in [0, 1]:
            karta = tk.Frame(souhrn, bg=BARVA_KARTA, padx=14, pady=10)
            karta.pack(side="left", fill="both", expand=True, padx=(0, 10 * (1 - b)))
            pocet = 0
            for radek in radky_kvestu[b]:
                if radek[2]:
                    pocet = pocet + 1
            self.popisek(karta, f"{SYMBOLY['Král'][b]}  {self.jmena[b]}  ·  kvesty {pocet}/{len(radky_kvestu[b])}",
                         12, "bold", BARVA_TEXT).pack(anchor="w", pady=(0, 4))
            for radek in radky_kvestu[b]:
                if radek[2]:
                    self.popisek(karta, "✓  " + radek[0], 11, "normal",
                                 BARVA_HOTOVO).pack(anchor="w")
                else:
                    self.popisek(karta, "○  " + radek[0] + "  (" + radek[1] + ")", 11,
                                 "normal", BARVA_TEXT_2).pack(anchor="w")

        self.popisek(ramec, "Zápis partie (PGN)", 11, "bold",
                     BARVA_TEXT_2).pack(anchor="w", pady=(12, 4))
        pole_pgn = scrolledtext.ScrolledText(ramec, width=70, height=9,
                                             font=(self.pismo_cisla, 11), wrap="word",
                                             bg=BARVA_POLE_TEXT, fg=BARVA_TEXT, relief="flat",
                                             highlightthickness=0, padx=10, pady=8)
        pole_pgn.insert("1.0", pgn_zapis)
        pole_pgn.config(state="disabled")      # jen pro čtení
        pole_pgn.pack(fill="x")

        tlacitka = tk.Frame(ramec, bg=BARVA_POZADI)
        tlacitka.pack(pady=(12, 0))
        self.tlacitko(tlacitka, "Nová hra", self.controller.nova_hra,
                      "hlavni").pack(side="left", padx=4)
        self.tlacitko(tlacitka, "Hlavní menu", self.controller.hlavni_menu,
                      "vedlejsi").pack(side="left", padx=4)
        self.tlacitko(tlacitka, "Zavřít", self.controller.zavri_aplikaci,
                      "vedlejsi").pack(side="left", padx=4)

    # ------------------------------------------------------------------
    # Vedlejší okna (pravidla, seznam kvestů, o hře)
    # Otevírají se jako samostatná okna, aby se nezavřela rozehraná partie.
    # ------------------------------------------------------------------

    def vytvor_okno(self, titulek, sirka, vyska):
        okno = tk.Toplevel(self.root)
        okno.title(titulek)
        okno.configure(bg=BARVA_POZADI)
        okno.geometry(f"{sirka}x{vyska}")
        okno.transient(self.root)          # okno patří k hlavnímu oknu
        return okno

    def textove_pole(self, okno):
        pole = scrolledtext.ScrolledText(okno, wrap="word", font=self.font(12, "normal"),
                                         bg=BARVA_KARTA, fg=BARVA_TEXT, relief="flat",
                                         highlightthickness=0, padx=20, pady=16,
                                         spacing1=2, spacing3=2)
        pole.tag_configure("nadpis", font=self.font(13, "bold"), foreground=BARVA_TEXT)
        pole.tag_configure("vedlejsi", foreground=BARVA_TEXT_2)
        return pole

    def zobraz_okno_pravidla(self):
        okno = self.vytvor_okno("Pravidla", 560, 560)
        pole = self.textove_pole(okno)
        pole.insert("1.0", TEXT_PRAVIDEL)
        pole.config(state="disabled")
        pole.pack(fill="both", expand=True, padx=MEZERA, pady=(MEZERA, 0))
        self.tlacitko(okno, "Zavřít", okno.destroy, "vedlejsi").pack(pady=MEZERA)

    def zobraz_okno_kvesty(self, radky):
        # radky = seznam [název, popis, obtížnost 1–3]
        okno = self.vytvor_okno("Seznam kvestů", 520, 600)
        self.popisek(okno, f"Zásoba kvestů ({len(radky)})", 18, "bold",
                     BARVA_TEXT).pack(anchor="w", padx=MEZERA, pady=(MEZERA, 0))
        self.popisek(okno, "V každé partii dostane hráč 4 z nich náhodně.", 11, "normal",
                     BARVA_TEXT_2).pack(anchor="w", padx=MEZERA, pady=(2, 10))
        pole = self.textove_pole(okno)
        for radek in radky:
            hvezdy = "★" * radek[2] + "☆" * (3 - radek[2])
            pole.insert("end", radek[0] + "  ", "nadpis")
            pole.insert("end", hvezdy + "\n", "vedlejsi")
            pole.insert("end", radek[1] + "\n\n")
        pole.config(state="disabled")
        pole.pack(fill="both", expand=True, padx=MEZERA)
        self.tlacitko(okno, "Zavřít", okno.destroy, "vedlejsi").pack(pady=MEZERA)

    def zobraz_okno_o_hre(self):
        okno = self.vytvor_okno("O hře", 380, 260)
        tk.Label(okno, text="♚", font=("Segoe UI Symbol", 40), bg=BARVA_POZADI,
                 fg=BARVA_TEXT).pack(pady=(MEZERA, 0))
        self.popisek(okno, "Šachy s kvesty", 18, "bold", BARVA_TEXT).pack()
        self.popisek(okno, "Školní projekt ChessWithQuests\nPython + tkinter, architektura MVC",
                     11, "normal", BARVA_TEXT_2).pack(pady=(4, 12))
        self.tlacitko(okno, "Zavřít", okno.destroy, "vedlejsi").pack()
