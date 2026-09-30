from model.figurka import Figurka

class Kral(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Král", barva, vektory_utoku, vektory)
        self.skok = False
        self.opakovat = False    # jen o jedno pole
        self.znacka = "K"
