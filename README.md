# ChessWithQuests
Školní projekt hry šachy s definovatelnými figurkami, hrací deskou a kvesty.
Společná repository všech studentů.

## Spuštění

```
python main.py
```

Hra potřebuje Python 3 s knihovnou tkinter (na Windows je součástí instalace Pythonu,
na Linuxu případně `sudo apt install python3-tk`). Záznamy partií se ukládají do složky `partie/`.

## Struktura (MVC)

- `model/` – figurky, herní plocha, tahy, pravidla (`RevizorTahu`), časovač, zápis partie
- `view/view.py` – `SachovniceView`, grafické rozhraní v tkinteru
- `controller/controller.py` – `HraController`, propojuje model a view
- `main.py` – spouštěcí skript
