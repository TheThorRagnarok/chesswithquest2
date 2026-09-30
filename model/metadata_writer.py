class MetadataWriter:
    # Ukládá metadata partie (hráči, datum, výsledek...)
    # a umí z nich vytvořit hlavičku ve formátu PGN, např. [White "Jan"]

    def __init__(self):
        self.metadata = []     # seznam dvojic [klic, hodnota]

    def method(self, typ):
        print(f"Zapisuji metadata typu: {typ}")

    def pridej_metadata(self, klic, hodnota):
        # Pokud klíč už existuje, přepíše hodnotu, jinak ho přidá
        for polozka in self.metadata:
            if polozka[0] == klic:
                polozka[1] = hodnota
                return
        self.metadata.append([klic, hodnota])

    def get_hlavicka(self):
        text = ""
        for polozka in self.metadata:
            text = text + "[" + polozka[0] + ' "' + str(polozka[1]) + '"]\n'
        return text
