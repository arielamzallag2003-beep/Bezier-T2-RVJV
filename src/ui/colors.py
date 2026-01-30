"""
Module Colors - Palette de couleurs pour l'application
"""

from dataclasses import dataclass
from typing import Tuple
import random


@dataclass(frozen=True)
class Color:
    """Représentation d'une couleur RGB"""
    r: int
    g: int
    b: int
    
    @property
    def rgb(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)
    
    @property
    def rgba(self) -> Tuple[int, int, int, int]:
        return (self.r, self.g, self.b, 255)
    
    def with_alpha(self, alpha: int) -> Tuple[int, int, int, int]:
        """Retourne la couleur avec un alpha spécifié"""
        return (self.r, self.g, self.b, alpha)
    
    def lighter(self, factor: float = 0.2) -> 'Color':
        """Retourne une version plus claire de la couleur"""
        return Color(
            min(255, int(self.r + (255 - self.r) * factor)),
            min(255, int(self.g + (255 - self.g) * factor)),
            min(255, int(self.b + (255 - self.b) * factor))
        )
    
    def darker(self, factor: float = 0.2) -> 'Color':
        """Retourne une version plus foncée de la couleur"""
        return Color(
            max(0, int(self.r * (1 - factor))),
            max(0, int(self.g * (1 - factor))),
            max(0, int(self.b * (1 - factor)))
        )
    
    def __iter__(self):
        return iter((self.r, self.g, self.b))


class ColorPalette:
    """Palette de couleurs principale de l'application"""
    
    # Couleurs de base Mathematica-style
    MATHEMATICA_BG = Color(250, 250, 250)
    MATHEMATICA_CARD = Color(255, 255, 255)
    MATHEMATICA_CARD_HOVER = Color(248, 248, 250)
    
    # Texte
    MATHEMATICA_TEXT = Color(33, 33, 33)
    MATHEMATICA_SUBTEXT = Color(117, 117, 117)
    
    # Bordures
    MATHEMATICA_BORDER = Color(221, 221, 221)
    
    # Accent orange
    MATHEMATICA_ORANGE = Color(221, 107, 32)
    MATHEMATICA_ORANGE_LIGHT = Color(238, 136, 68)
    MATHEMATICA_ORANGE_DARK = Color(180, 80, 20)
    
    # Couleurs pour les polygones
    POLYGON_DEFAULT = Color(100, 149, 237)  # Cornflower Blue
    POLYGON_CLIPPED = Color(50, 205, 50)     # Lime Green
    POLYGON_FILLED = Color(138, 43, 226)     # Blue Violet
    
    # Fenêtre de clipping
    WINDOW_BORDER = Color(220, 20, 60)       # Crimson
    WINDOW_FILL = Color(255, 200, 200)
    
    # Sommets
    VERTEX_DEFAULT = Color(50, 50, 50)
    VERTEX_SELECTED = Color(255, 0, 0)
    VERTEX_HOVER = Color(255, 165, 0)
    
    # Grille
    GRID_MAJOR = Color(200, 200, 200)
    GRID_MINOR = Color(230, 230, 230)
    
    # États
    SUCCESS = Color(46, 204, 113)
    WARNING = Color(241, 196, 15)
    ERROR = Color(231, 76, 60)
    INFO = Color(52, 152, 219)
    
    # Thème sombre (pour future utilisation)
    DARK_BG = Color(20, 20, 30)
    DARKER_BG = Color(10, 10, 15)
    PANEL_BG = Color(30, 30, 45)
    
    # Texte sur fond sombre
    TEXT_PRIMARY = Color(255, 255, 255)
    TEXT_SECONDARY = Color(200, 200, 200)
    TEXT_DISABLED = Color(120, 120, 120)
    
    # Boutons
    BUTTON_NORMAL = Color(60, 60, 80)
    BUTTON_HOVER = Color(80, 80, 100)
    BUTTON_ACTIVE = Color(100, 100, 120)
    BUTTON_DISABLED = Color(45, 45, 60)
    
    # Or/Gold (pour accents)
    GOLD = Color(218, 165, 32)
    DARK_GOLD = Color(184, 134, 11)
    LIGHT_GOLD = Color(255, 215, 0)
    
    # Couleurs des polygones (pour rotation automatique)
    POLYGON_COLORS = [
        Color(65, 105, 225),    # Royal Blue
        Color(50, 205, 50),     # Lime Green
        Color(255, 165, 0),     # Orange
        Color(238, 130, 238),   # Violet
        Color(0, 206, 209),     # Dark Turquoise
        Color(255, 99, 71),     # Tomato
        Color(147, 112, 219),   # Medium Purple
        Color(60, 179, 113),    # Medium Sea Green
        Color(255, 20, 147),    # Deep Pink
        Color(0, 191, 255),     # Deep Sky Blue
        Color(255, 215, 0),     # Gold
        Color(127, 255, 0),     # Chartreuse
    ]
    
    @classmethod
    def get_polygon_color(cls, index: int) -> Color:
        """Retourne une couleur de polygone basée sur l'index"""
        return cls.POLYGON_COLORS[index % len(cls.POLYGON_COLORS)]
    
    @classmethod
    def random_color(cls) -> Color:
        """Génère une couleur aléatoire vive"""
        h = random.random()
        s = 0.7 + random.random() * 0.3  # Saturation élevée
        v = 0.8 + random.random() * 0.2  # Luminosité élevée
        
        # Conversion HSV -> RGB
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        
        i = i % 6
        if i == 0:
            r, g, b = v, t, p
        elif i == 1:
            r, g, b = q, v, p
        elif i == 2:
            r, g, b = p, v, t
        elif i == 3:
            r, g, b = p, q, v
        elif i == 4:
            r, g, b = t, p, v
        else:
            r, g, b = v, p, q
        
        return Color(int(r * 255), int(g * 255), int(b * 255))
    
    @classmethod
    def interpolate(cls, color1: Color, color2: Color, t: float) -> Color:
        """Interpole entre deux couleurs (t entre 0 et 1)"""
        t = max(0, min(1, t))
        return Color(
            int(color1.r + (color2.r - color1.r) * t),
            int(color1.g + (color2.g - color1.g) * t),
            int(color1.b + (color2.b - color1.b) * t)
        )


# Alias pour compatibilité
Colors = ColorPalette