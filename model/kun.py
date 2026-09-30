from model.figurka import Figurka

class Kun(Figurka):
    def __init__(self, barva):
        vektory = [
            [-2, -1], [-2, 1],
            [-1, -2], [-1, 2],
            [1, -2],  [1, 2],
            [2, -1],  [2, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Kůň", barva, vektory_utoku, vektory)
        self.skok = True
        self.opakovat = False    # skočí jen jednou
        self.znacka = "N"
