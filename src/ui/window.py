from dataclasses import dataclass


@dataclass
class WindowConfig:
    width: int = 1200
    height: int = 800
    title: str = "Fenêtrage & Remplissage de Polygones"
    fps: int = 60
