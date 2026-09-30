class GameLogger:
    def __init__(self, soubor):
        self.soubor = soubor

    def uloz_tah(self, tah):
        # Připíše jeden tah na konec souboru
        with open(self.soubor, "a", encoding="utf-8") as f:
            f.write(str(tah) + "\n")

    def uloz_text(self, text):
        # Připíše libovolný text (např. celý PGN zápis na konci partie)
        with open(self.soubor, "a", encoding="utf-8") as f:
            f.write(text + "\n")

    def vytvor_soubor(self, nazev):
        self.soubor = nazev
        with open(self.soubor, "w", encoding="utf-8") as f:
            f.write("")
        print(f"Soubor {self.soubor} vytvořen.")
