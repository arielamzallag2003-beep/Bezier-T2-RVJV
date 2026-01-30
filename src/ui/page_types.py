"""
Module Page Types - Définition des types de pages et modes
"""

from enum import Enum, auto


class PageType(Enum):
    """Types de pages disponibles dans l'application"""
    HOME = auto()
    POLYGON_WORKSPACE = auto()  # Page principale pour polygones
    BEZIER_WORKSPACE = auto()   # Page pour courbes de Bézier (T2)
    MATRIX = auto()             # Page pour les opérations matricielles


class PolygonMode(Enum):
    """Modes disponibles dans l'espace de travail polygone"""
    DRAWING = auto()      # Dessin de polygones
    WINDOW = auto()       # Dessin de la fenêtre de clipping
    SELECT = auto()       # Sélection de polygones
    EDIT = auto()         # Édition de sommets
    CLIPPING = auto()     # Fenêtrage actif
    FILLING = auto()      # Remplissage actif
    BOTH = auto()         # Fenêtrage puis remplissage


class BezierMode(Enum):
    """Modes disponibles dans l'espace de travail Bézier (pour T2)"""
    DRAW_CONTROL = auto()     # Dessiner des points de contrôle
    SELECT_CURVE = auto()     # Sélectionner une courbe
    EDIT_CONTROL = auto()     # Éditer les points de contrôle
    TRANSFORM = auto()        # Appliquer des transformations
    CONNECT = auto()          # Raccorder des courbes (C0, C1, C2)


class TransformType(Enum):
    """Types de transformations géométriques"""
    TRANSLATION = auto()
    ROTATION = auto()
    SCALING = auto()
    SHEARING = auto()
    REFLECTION_X = auto()
    REFLECTION_Y = auto()


class ContinuityType(Enum):
    """Types de continuité pour les raccordements de Bézier"""
    C0 = auto()  # Continuité de position (les courbes se touchent)
    C1 = auto()  # Continuité de tangente (dérivée première)
    C2 = auto()  # Continuité de courbure (dérivée seconde)


class AlgorithmType(Enum):
    """Types d'algorithmes disponibles"""
    # Polygones
    SUTHERLAND_HODGMAN = auto()  # Fenêtrage
    LCA_FILL = auto()            # Remplissage
    
    # Bézier
    DIRECT_FORMULA = auto()      # Formule directe avec Pascal
    DE_CASTELJAU = auto()        # Algorithme de Casteljau
    
    # Enveloppe convexe
    JARVIS_MARCH = auto()        # Marche de Jarvis (gift wrapping)
    GRAHAM_SCAN = auto()         # Parcours de Graham