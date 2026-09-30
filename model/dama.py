from model.figurka import Figurka

class Dama(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, 0], [1, 0], [0, -1], [0, 1],   # jako věž
            [-1, -1], [-1, 1], [1, -1], [1, 1]  # jako střelec
        ]
        vektory_utoku = vektory
        super().__init__("Dáma", barva, vektory_utoku, vektory)
        self.skok = False
        self.opakovat = True     # jde libovolně daleko
        self.znacka = "Q"
