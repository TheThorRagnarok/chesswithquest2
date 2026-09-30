from model.metadata_writer import MetadataWriter

class ChessNotationWriter(MetadataWriter):
    def __init__(self, format_notace):
        super().__init__()
        self.format_notace = format_notace
        self.zaznam_hry = []      # seznam záznamů [cislo_tahu, barva_hrace, text_tahu]
        self.vysledek = ""        # "1-0", "0-1", "1/2-1/2" nebo "" (hra běží)

    def method(self, typ):
        print(f"Zapis notace formátu {self.format_notace}: {typ}")

    def pridej_tah(self, tah, cislo_tahu, barva_hrace):
        # Uloží tah ve formátu "e2-e4" (dlouhá algebraická notace)
        self.zaznam_hry.append([cislo_tahu, barva_hrace, tah.na_notaci()])

    def pridej_znacku(self, znacka):
        # Přidá k poslednímu tahu "+" (šach) nebo "#" (mat)
        if len(self.zaznam_hry) > 0:
            posledni = self.zaznam_hry[len(self.zaznam_hry) - 1]
            posledni[2] = posledni[2] + znacka

    def nastav_vysledek(self, vysledek):
        self.vysledek = vysledek
        self.pridej_metadata("Result", vysledek)

    def get_pgn_zapis(self):
        # Vrátí zápis ve tvaru "1. e2-e4 e7-e5  2. d2-d4 d7-d5  ..."
        text = ""
        for zaznam in self.zaznam_hry:
            cislo_tahu = zaznam[0]
            barva_hrace = zaznam[1]
            notace = zaznam[2]
            if barva_hrace == 0:
                if text != "":
                    text = text + "  "
                text = text + str(cislo_tahu) + ". " + notace
            else:
                text = text + " " + notace
        if self.vysledek != "":
            text = text + "  " + self.vysledek
        return text

    def get_cely_zapis(self):
        # Hlavička s metadaty + zápis tahů
        return self.get_hlavicka() + "\n" + self.get_pgn_zapis() + "\n"

    def __str__(self):
        return f"ChessNotationWriter ({self.format_notace})"
