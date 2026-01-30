"""
Module Point - Représentation d'un point 2D
Principe SOLID: Single Responsibility - gère uniquement les points
"""

from dataclasses import dataclass
from typing import Tuple
import math


@dataclass
class Point:
    """
    Représentation d'un point dans le plan 2D
    """
    x: float
    y: float
    
    def __iter__(self):
        """Permet d'utiliser Point comme tuple"""
        return iter((self.x, self.y))
    
    def __add__(self, other: 'Point') -> 'Point':
        """Addition de deux points"""
        return Point(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Point') -> 'Point':
        """Soustraction de deux points (crée un vecteur)"""
        return Point(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Point':
        """Multiplication par un scalaire"""
        return Point(self.x * scalar, self.y * scalar)
    
    def __rmul__(self, scalar: float) -> 'Point':
        """Multiplication par un scalaire (ordre inversé)"""
        return self.__mul__(scalar)
    
    def dot(self, other: 'Point') -> float:
        """
        Produit scalaire avec un autre point/vecteur
        Utilisé pour déterminer les angles et la perpendicularité
        """
        return self.x * other.x + self.y * other.y
    
    def cross(self, other: 'Point') -> float:
        """
        Produit vectoriel 2D (déterminant)
        Utilisé pour déterminer l'orientation et les intersections
        """
        return self.x * other.y - self.y * other.x
    
    def magnitude(self) -> float:
        """Calcule la norme (longueur) du vecteur"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def distance_to(self, other: 'Point') -> float:
        """Calcule la distance à un autre point"""
        return (self - other).magnitude()
    
    def normalize(self) -> 'Point':
        """Retourne un vecteur normalisé (longueur 1)"""
        mag = self.magnitude()
        if mag == 0:
            return Point(0, 0)
        return Point(self.x / mag, self.y / mag)
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convertit en tuple"""
        return (self.x, self.y)
    
    def to_int_tuple(self) -> Tuple[int, int]:
        """Convertit en tuple d'entiers (pour pygame)"""
        return (int(self.x), int(self.y))
    
    @classmethod
    def from_tuple(cls, t: Tuple[float, float]) -> 'Point':
        """Crée un Point à partir d'un tuple"""
        return cls(t[0], t[1])
    
    def __repr__(self) -> str:
        return f"Point({self.x:.2f}, {self.y:.2f})"
