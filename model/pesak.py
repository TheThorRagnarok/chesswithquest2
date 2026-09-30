from model.figurka import Figurka

class Pesak(Figurka):
    def __init__(self, barva):
        # bílý jde nahoru (záporné řádky), černý dolů (kladné řádky)
        if barva == 0:
            vektory = [[-1, 0]]
            vektory_utoku = [[-1, -1], [-1, 1]]
        else:
            vektory = [[1, 0]]
            vektory_utoku = [[1, -1], [1, 1]]
        super().__init__("Pěšák", barva, vektory_utoku, vektory)
        self.skok = False
        self.opakovat = False    # pohyb pěšáka řeší RevizorTahu zvlášť
        self.znacka = ""
