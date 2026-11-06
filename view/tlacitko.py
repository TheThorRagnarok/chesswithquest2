import tkinter as tk


class Tlacitko(tk.Label):
    # Vlastní tlačítko postavené na tk.Label (dědičnost).
    #
    # Proč ne obyčejné tk.Button?
    #  - na macOS tk.Button ignoruje barvu pozadí, takže by tlačítka
    #    vypadala na každém systému jinak (a bílý text na bílém nešel vidět),
    #  - u Labelu si barvy i chování při najetí/stisku řídíme sami.
    #
    # Chování (podle zásad Apple pro tlačítka):
    #  - zbarví se hned při STISKU myši, ne až po puštění,
    #  - akce se provede až po puštění, a jen když je myš pořád nad tlačítkem
    #    (když hráč myš odtáhne pryč, kliknutí se zruší).

    def __init__(self, rodic, text, prikaz, barvy, pismo, hodnota=None):
        # barvy = [pozadí, pozadí při najetí, pozadí při stisku, barva textu]
        super().__init__(rodic, text=text, font=pismo, padx=18, pady=9, cursor="hand2")
        self.prikaz = prikaz          # metoda, která se zavolá po kliknutí
        self.hodnota = hodnota        # volitelný parametr pro prikaz
        self.nastav_barvy(barvy)

        self.bind("<Enter>", self.najeti)
        self.bind("<Leave>", self.odjeti)
        self.bind("<ButtonPress-1>", self.stisk)
        self.bind("<ButtonRelease-1>", self.uvolneni)

    def nastav_barvy(self, barvy):
        self.barva = barvy[0]
        self.barva_najeti = barvy[1]
        self.barva_stisk = barvy[2]
        self.config(bg=self.barva, fg=barvy[3])

    def najeti(self, udalost):
        self.config(bg=self.barva_najeti)

    def odjeti(self, udalost):
        self.config(bg=self.barva)

    def stisk(self, udalost):
        self.config(bg=self.barva_stisk)

    def uvolneni(self, udalost):
        # Je myš při puštění pořád nad tlačítkem?
        uvnitr = 0 <= udalost.x < self.winfo_width() and 0 <= udalost.y < self.winfo_height()
        if not uvnitr:
            self.config(bg=self.barva)
            return
        self.config(bg=self.barva_najeti)
        # Akce může tlačítko smazat (přepnutí obrazovky),
        # proto ji voláme až úplně na konci.
        if self.hodnota is None:
            self.prikaz()
        else:
            self.prikaz(self.hodnota)
