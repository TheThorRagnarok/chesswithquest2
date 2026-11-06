# ChessWithQuests
Školní projekt hry šachy s definovatelnými figurkami, hrací deskou a kvesty.
Společná repository všech studentů.

## Spuštění

```
python main.py
```

Po spuštění se objeví hlavní menu (Nová hra, Seznam kvestů, Pravidla, Ukončit).
Stejné akce jsou i v horní liště okna (Hra, Nápověda).

## Kvesty

V zásobě je 24 kvestů (`model/kwest_manager.py`). Na začátku partie dostane každý hráč
4 náhodné. Vyhrát jde matem, nebo tím, že hráč jako první splní všechny své 4 kvesty.
Po každém tahu se do `StatistikaHrace` zapíše, co se v tahu stalo (braní, šach, rošáda…),
a kvest se splní, když příslušné počítadlo dosáhne cíle.

Hra potřebuje Python 3 s knihovnou tkinter (na Windows je součástí instalace Pythonu,
na Linuxu případně `sudo apt install python3-tk`). Záznamy partií se ukládají do složky `partie/`.

## Struktura (MVC)

- `model/` – figurky, herní plocha, tahy, pravidla (`RevizorTahu`), časovač, zápis partie
- `view/view.py` – `SachovniceView`, grafické rozhraní v tkinteru
- `view/tlacitko.py` – `Tlacitko`, vlastní tlačítko (stejný vzhled na Windows i macOS)
- `controller/controller.py` – `HraController`, propojuje model a view
- `main.py` – spouštěcí skript
