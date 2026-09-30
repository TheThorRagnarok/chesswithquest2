class GameTimer:
    # Šachové hodiny pro dva hráče.
    # Samotné "tikání" zajišťuje controller přes tkinter after(),
    # tato třída si jen pamatuje zbývající čas.

    def __init__(self, cas_limit_sekundy):
        self.cas_limit = cas_limit_sekundy
        self.cas_bily = cas_limit_sekundy     # zbývající sekundy bílého
        self.cas_cerny = cas_limit_sekundy    # zbývající sekundy černého
        self.aktivni_hrac = 0                 # 0 = bílý, 1 = černý (komu teče čas)

    def odecti_sekundu(self):
        # Odečte 1 sekundu aktivnímu hráči a vrátí jeho zbývající čas
        if self.aktivni_hrac == 0:
            if self.cas_bily > 0:
                self.cas_bily = self.cas_bily - 1
            return self.cas_bily
        else:
            if self.cas_cerny > 0:
                self.cas_cerny = self.cas_cerny - 1
            return self.cas_cerny

    def na_text(self, sekundy):
        # 125 -> "02:05"
        minuty = sekundy // 60
        zbytek = sekundy % 60
        return f"{minuty:02d}:{zbytek:02d}"

    def get_cas_bily(self):
        return self.na_text(self.cas_bily)

    def get_cas_cerny(self):
        return self.na_text(self.cas_cerny)

    def prepni_hrace(self, hrac):
        # hrac = 0 (bílý) nebo 1 (černý)
        self.aktivni_hrac = hrac

    def __str__(self):
        return f"GameTimer bílý {self.get_cas_bily()}, černý {self.get_cas_cerny()}"
