import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext

# Rozměry šachovnice na obrazovce
VELIKOST_POLE = 64           # velikost jednoho pole v pixelech
OKRAJ = 24                   # okraj kolem desky pro popisky a–h a 1–8

# Barvy
BARVA_SVETLA = "#F0D9B5"
BARVA_TMAVA = "#B58863"
BARVA_VYBRANE = "#F6F669"    # označená figurka
BARVA_TAH = "#4CAF50"        # tečka / kroužek pro možný tah
BARVA_POZADI = "#EDE6DA"

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


class SachovniceView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.root.title("Šachy")
        self.root.configure(bg=BARVA_POZADI)
        self.root.resizable(False, False)

        # stav herní obrazovky
        self.herni_deska = None
        self.vybrane_pole = None          # [radek, sloupec] označené figurky
        self.zvyraznena_pole = []         # seznam polí možných tahů
        self.canvas = None

    # ------------------------------------------------------------------
    # Pomocné metody
    # ------------------------------------------------------------------

    def vycisti_okno(self):
        # Smaže všechny prvky v okně (před přepnutím obrazovky)
        for prvek in self.root.winfo_children():
            prvek.destroy()
        self.canvas = None

    def symbol_figurky(self, figurka):
        return SYMBOLY[figurka.nazev][figurka.barva]

    def potvrd(self, titulek, otazka):
        # Zobrazí dialog Ano/Ne a vrátí True/False
        return messagebox.askyesno(titulek, otazka)

    # ------------------------------------------------------------------
    # Úvodní obrazovka
    # ------------------------------------------------------------------

    def zobraz_uvodni_obrazovku(self):
        self.vycisti_okno()

        ramec = tk.Frame(self.root, bg=BARVA_POZADI, padx=40, pady=30)
        ramec.pack()

        tk.Label(ramec, text="♔ Šachy ♚", font=("Arial", 28, "bold"),
                 bg=BARVA_POZADI).grid(row=0, column=0, columnspan=2, pady=(0, 20))

        tk.Label(ramec, text="Hráč 1 (bílý):", font=("Arial", 12),
                 bg=BARVA_POZADI).grid(row=1, column=0, sticky="e", pady=5)
        self.pole_jmeno1 = tk.Entry(ramec, font=("Arial", 12), width=20)
        self.pole_jmeno1.insert(0, "Hráč 1")
        self.pole_jmeno1.grid(row=1, column=1, pady=5)

        tk.Label(ramec, text="Hráč 2 (černý):", font=("Arial", 12),
                 bg=BARVA_POZADI).grid(row=2, column=0, sticky="e", pady=5)
        self.pole_jmeno2 = tk.Entry(ramec, font=("Arial", 12), width=20)
        self.pole_jmeno2.insert(0, "Hráč 2")
        self.pole_jmeno2.grid(row=2, column=1, pady=5)

        tk.Label(ramec, text="Délka hry:", font=("Arial", 12),
                 bg=BARVA_POZADI).grid(row=3, column=0, sticky="ne", pady=(15, 5))
        self.delka_hry = tk.IntVar(value=5)
        ramec_casu = tk.Frame(ramec, bg=BARVA_POZADI)
        ramec_casu.grid(row=3, column=1, sticky="w", pady=(15, 5))
        moznosti = [[2, "2 minuty"], [5, "5 minut"], [10, "10 minut"]]
        for moznost in moznosti:
            tk.Radiobutton(ramec_casu, text=moznost[1], variable=self.delka_hry,
                           value=moznost[0], font=("Arial", 12),
                           bg=BARVA_POZADI).pack(anchor="w")

        self.chyba_uvod = tk.Label(ramec, text="", fg="red", font=("Arial", 11),
                                   bg=BARVA_POZADI)
        self.chyba_uvod.grid(row=4, column=0, columnspan=2, pady=5)

        tk.Button(ramec, text="Spustit hru", font=("Arial", 14, "bold"),
                  bg="#4CAF50", fg="white", padx=20, pady=5,
                  command=self.stisk_spustit).grid(row=5, column=0, columnspan=2, pady=10)

    def stisk_spustit(self):
        # Obsluha tlačítka "Spustit hru"
        jmeno1 = self.pole_jmeno1.get().strip()
        jmeno2 = self.pole_jmeno2.get().strip()
        if jmeno1 == "" or jmeno2 == "":
            self.chyba_uvod.config(text="Zadej jména obou hráčů.")
            return
        self.controller.zacni_hru(jmeno1, jmeno2, self.delka_hry.get())

    # ------------------------------------------------------------------
    # Herní obrazovka
    # ------------------------------------------------------------------

    def zobraz_herni_obrazovku(self, jmeno_bileho, jmeno_cerneho):
        self.vycisti_okno()
        self.vybrane_pole = None
        self.zvyraznena_pole = []

        hlavni = tk.Frame(self.root, bg=BARVA_POZADI, padx=10, pady=10)
        hlavni.pack()

        # --- šachovnice vlevo ---
        velikost = 8 * VELIKOST_POLE + 2 * OKRAJ
        self.canvas = tk.Canvas(hlavni, width=velikost, height=velikost,
                                bg=BARVA_POZADI, highlightthickness=0)
        self.canvas.grid(row=0, column=0)
        self.canvas.bind("<Button-1>", self.klik_na_canvas)

        # --- panel vpravo ---
        panel = tk.Frame(hlavni, bg=BARVA_POZADI, padx=15)
        panel.grid(row=0, column=1, sticky="n")

        tk.Label(panel, text="Na tahu:", font=("Arial", 11),
                 bg=BARVA_POZADI).pack(anchor="w")
        self.label_aktivni = tk.Label(panel, text="", font=("Arial", 14, "bold"),
                                      bg=BARVA_POZADI)
        self.label_aktivni.pack(anchor="w", pady=(0, 15))

        # hodiny
        self.label_cas_cerny = tk.Label(panel, text="", font=("Courier", 16, "bold"),
                                        width=22, anchor="w", padx=5, pady=3)
        self.label_cas_cerny.pack(anchor="w", pady=2)
        self.label_cas_bily = tk.Label(panel, text="", font=("Courier", 16, "bold"),
                                       width=22, anchor="w", padx=5, pady=3)
        self.label_cas_bily.pack(anchor="w", pady=2)
        self.jmeno_bileho = jmeno_bileho
        self.jmeno_cerneho = jmeno_cerneho

        # vyhozené figurky
        tk.Label(panel, text="Vyhozené figurky:", font=("Arial", 11, "bold"),
                 bg=BARVA_POZADI).pack(anchor="w", pady=(15, 0))
        self.label_vyhozene_b = tk.Label(panel, text="", font=("Segoe UI Symbol", 18),
                                         bg=BARVA_POZADI, wraplength=260, justify="left")
        self.label_vyhozene_b.pack(anchor="w")
        self.label_vyhozene_c = tk.Label(panel, text="", font=("Segoe UI Symbol", 18),
                                         bg=BARVA_POZADI, wraplength=260, justify="left")
        self.label_vyhozene_c.pack(anchor="w")

        # zprávy pro hráče
        tk.Label(panel, text="Zpráva:", font=("Arial", 11, "bold"),
                 bg=BARVA_POZADI).pack(anchor="w", pady=(15, 0))
        self.label_zprava = tk.Label(panel, text="", font=("Arial", 13),
                                     fg="#B22222", bg=BARVA_POZADI,
                                     wraplength=260, justify="left")
        self.label_zprava.pack(anchor="w")

        # tlačítka
        tk.Button(panel, text="Vzdát se", font=("Arial", 12), width=14,
                  command=self.controller.vzdani_se).pack(anchor="w", pady=(25, 5))
        tk.Button(panel, text="Nová hra", font=("Arial", 12), width=14,
                  command=self.controller.nova_hra).pack(anchor="w", pady=5)

        self.zobraz_vyhozene([], [])

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

                # barva pole – světlá a tmavá se střídají
                if (radek + sloupec) % 2 == 0:
                    barva = BARVA_SVETLA
                else:
                    barva = BARVA_TMAVA
                if self.vybrane_pole == [radek, sloupec]:
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
                if [radek, sloupec] in self.zvyraznena_pole:
                    if figurka is None:
                        # prázdné pole -> zelená tečka
                        r = 9
                        self.canvas.create_oval(stred_x - r, stred_y - r, stred_x + r, stred_y + r,
                                                fill=BARVA_TAH, outline=BARVA_TAH)
                    else:
                        # figurku lze sebrat -> zelený rámeček
                        self.canvas.create_rectangle(x + 2, y + 2,
                                                     x + VELIKOST_POLE - 2, y + VELIKOST_POLE - 2,
                                                     outline=BARVA_TAH, width=4)

        # popisky sloupců (a–h) a řádků (8–1)
        for i in range(8):
            stred = OKRAJ + i * VELIKOST_POLE + VELIKOST_POLE // 2
            konec = OKRAJ + 8 * VELIKOST_POLE
            self.canvas.create_text(stred, OKRAJ // 2, text=pismena[i], font=("Arial", 11))
            self.canvas.create_text(stred, konec + OKRAJ // 2, text=pismena[i], font=("Arial", 11))
            self.canvas.create_text(OKRAJ // 2, stred, text=str(8 - i), font=("Arial", 11))
            self.canvas.create_text(konec + OKRAJ // 2, stred, text=str(8 - i), font=("Arial", 11))

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

    def zobraz_aktivniho_hrace(self, jmeno, barva):
        # Ukáže, kdo je na tahu, a zvýrazní jeho hodiny
        if barva == 0:
            self.label_aktivni.config(text=f"{jmeno} (bílý)")
            self.label_cas_bily.config(bg="#FFFFFF", fg="black", relief="solid", bd=1)
            self.label_cas_cerny.config(bg=BARVA_POZADI, fg="#777777", relief="flat", bd=1)
        else:
            self.label_aktivni.config(text=f"{jmeno} (černý)")
            self.label_cas_cerny.config(bg="#333333", fg="white", relief="solid", bd=1)
            self.label_cas_bily.config(bg=BARVA_POZADI, fg="#777777", relief="flat", bd=1)

    def aktualizuj_cas(self, cas_bile, cas_cerne):
        # cas_bile a cas_cerne jsou texty ve formátu "MM:SS"
        self.label_cas_bily.config(text=f"♔ {cas_bile}  {self.jmeno_bileho}")
        self.label_cas_cerny.config(text=f"♚ {cas_cerne}  {self.jmeno_cerneho}")

    def zobraz_zpravu(self, zprava):
        self.label_zprava.config(text=zprava)

    def zobraz_vyhozene(self, figurky_b, figurky_c):
        # figurky_b = vyhozené bílé figurky, figurky_c = vyhozené černé figurky
        text_b = ""
        for figurka in figurky_b:
            text_b = text_b + self.symbol_figurky(figurka)
        text_c = ""
        for figurka in figurky_c:
            text_c = text_c + self.symbol_figurky(figurka)
        if text_b == "":
            text_b = "–"
        if text_c == "":
            text_c = "–"
        self.label_vyhozene_b.config(text="Bílé: " + text_b)
        self.label_vyhozene_c.config(text="Černé: " + text_c)

    # ------------------------------------------------------------------
    # Koncová obrazovka
    # ------------------------------------------------------------------

    def zobraz_konec(self, vitez, pgn_zapis):
        # vitez = text s výsledkem (např. "Vyhrál Jan (bílý) – mat")
        self.vycisti_okno()

        ramec = tk.Frame(self.root, bg=BARVA_POZADI, padx=30, pady=20)
        ramec.pack()

        tk.Label(ramec, text="Konec hry", font=("Arial", 24, "bold"),
                 bg=BARVA_POZADI).pack(pady=(0, 10))
        tk.Label(ramec, text=vitez, font=("Arial", 14), bg=BARVA_POZADI,
                 wraplength=500, justify="center").pack(pady=(0, 15))

        tk.Label(ramec, text="Zápis partie (PGN):", font=("Arial", 11, "bold"),
                 bg=BARVA_POZADI).pack(anchor="w")
        pole_pgn = scrolledtext.ScrolledText(ramec, width=60, height=15,
                                             font=("Courier", 11), wrap="word")
        pole_pgn.insert("1.0", pgn_zapis)
        pole_pgn.config(state="disabled")      # jen pro čtení
        pole_pgn.pack(pady=5)

        tlacitka = tk.Frame(ramec, bg=BARVA_POZADI)
        tlacitka.pack(pady=10)
        tk.Button(tlacitka, text="Nová hra", font=("Arial", 12), width=12,
                  command=self.controller.nova_hra).pack(side="left", padx=10)
        tk.Button(tlacitka, text="Zavřít", font=("Arial", 12), width=12,
                  command=self.controller.zavri_aplikaci).pack(side="left", padx=10)
