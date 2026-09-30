from model.figurka import Figurka

class Vez(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, 0], [1, 0],    # svisle
            [0, -1], [0, 1]     # vodorovně
        ]
        vektory_utoku = vektory
        super().__init__("Věž", barva, vektory_utoku, vektory)
        self.skok = False
        self.opakovat = True     # jde libovolně daleko
        self.znacka = "R"
