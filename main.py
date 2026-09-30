import tkinter as tk
from controller.controller import HraController

if __name__ == "__main__":
    root = tk.Tk()
    hra = HraController(root)
    root.mainloop()
