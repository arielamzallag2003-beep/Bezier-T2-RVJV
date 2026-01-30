"""
Module Math Utils - Utilitaires mathématiques avancés
Inclut les matrices de transformation pour le projet T2 (Bézier)
"""

import math
from typing import Tuple, Optional, List
from src.core.point import Point


class MathUtils:
    """Utilitaires mathématiques de base"""
    
    @staticmethod
    def dot_product(v1: Point, v2: Point) -> float:
        """Produit scalaire de deux vecteurs"""
        return v1.x * v2.x + v1.y * v2.y
    
    @staticmethod
    def cross_product(v1: Point, v2: Point) -> float:
        """Produit vectoriel 2D (déterminant)"""
        return v1.x * v2.y - v1.y * v2.x
    
    @staticmethod
    def is_point_left_of_edge(point: Point, edge_start: Point, edge_end: Point) -> bool:
        """Vérifie si un point est à gauche d'une arête"""
        edge_vec = edge_end - edge_start
        point_vec = point - edge_start
        return MathUtils.cross_product(edge_vec, point_vec) > 0
    
    @staticmethod
    def compute_line_intersection(
        p1: Point, p2: Point,
        p3: Point, p4: Point
    ) -> Optional[Point]:
        """
        Calcule l'intersection de deux lignes (p1-p2) et (p3-p4)
        Retourne None si les lignes sont parallèles
        """
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) < 1e-10:
            return None  # Lignes parallèles
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        
        return Point(
            x1 + t * (x2 - x1),
            y1 + t * (y2 - y1)
        )
    
    @staticmethod
    def compute_segment_intersection(
        p1: Point, p2: Point,
        p3: Point, p4: Point
    ) -> Optional[Point]:
        """
        Calcule l'intersection de deux segments [p1-p2] et [p3-p4]
        Retourne None si les segments ne s'intersectent pas
        """
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) < 1e-10:
            return None
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            return Point(
                x1 + t * (x2 - x1),
                y1 + t * (y2 - y1)
            )
        
        return None
    
    @staticmethod
    def point_on_segment(p1: Point, p2: Point, t: float) -> Point:
        """Interpolation linéaire entre deux points"""
        return Point(
            (1 - t) * p1.x + t * p2.x,
            (1 - t) * p1.y + t * p2.y
        )
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """Interpolation linéaire entre deux valeurs"""
        return a + (b - a) * t
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """Limite une valeur entre min et max"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def compute_normal(edge_start: Point, edge_end: Point, is_clockwise: bool = False) -> Point:
        """Calcule la normale d'une arête"""
        edge = edge_end - edge_start
        
        if is_clockwise:
            normal = Point(edge.y, -edge.x)
        else:
            normal = Point(-edge.y, edge.x)
        
        return normal.normalize()
    
    @staticmethod
    def polygon_area(vertices: List[Point]) -> float:
        """Calcule l'aire d'un polygone (formule du lacet)"""
        if len(vertices) < 3:
            return 0.0
        
        area = 0.0
        n = len(vertices)
        
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i].x * vertices[j].y
            area -= vertices[j].x * vertices[i].y
        
        return abs(area) / 2.0
    
    @staticmethod
    def polygon_centroid(vertices: List[Point]) -> Point:
        """Calcule le centroïde d'un polygone"""
        if len(vertices) == 0:
            return Point(0, 0)
        
        cx = sum(p.x for p in vertices) / len(vertices)
        cy = sum(p.y for p in vertices) / len(vertices)
        return Point(cx, cy)
    
    @staticmethod
    def is_polygon_clockwise(vertices: List[Point]) -> bool:
        """Vérifie si un polygone est défini dans le sens horaire"""
        if len(vertices) < 3:
            return False
        
        signed_area = 0.0
        n = len(vertices)
        
        for i in range(n):
            j = (i + 1) % n
            signed_area += vertices[i].x * vertices[j].y
            signed_area -= vertices[j].x * vertices[i].y
        
        return signed_area < 0
    
    @staticmethod
    def angle_between_vectors(v1: Point, v2: Point) -> float:
        """Calcule l'angle entre deux vecteurs en radians"""
        dot = v1.dot(v2)
        mag1 = v1.magnitude()
        mag2 = v2.magnitude()
        
        if mag1 == 0 or mag2 == 0:
            return 0
        
        cos_angle = MathUtils.clamp(dot / (mag1 * mag2), -1, 1)
        return math.acos(cos_angle)
    
    @staticmethod
    def distance_point_to_line(point: Point, line_start: Point, line_end: Point) -> float:
        """Calcule la distance d'un point à une ligne"""
        line_vec = line_end - line_start
        point_vec = point - line_start
        
        line_len_sq = line_vec.x ** 2 + line_vec.y ** 2
        if line_len_sq == 0:
            return point.distance_to(line_start)
        
        cross = abs(MathUtils.cross_product(line_vec, point_vec))
        return cross / math.sqrt(line_len_sq)


class Matrix3x3:
    """
    Matrice 3x3 pour les transformations 2D homogènes
    Utilisée pour translation, rotation, mise à l'échelle, cisaillement
    """
    
    def __init__(self, values: List[List[float]] = None):
        """
        Initialise la matrice
        Par défaut: matrice identité
        """
        if values is None:
            self.m = [
                [1.0, 0.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0]
            ]
        else:
            self.m = [row[:] for row in values]
    
    @classmethod
    def identity(cls) -> 'Matrix3x3':
        """Retourne la matrice identité"""
        return cls()
    
    @classmethod
    def translation(cls, tx: float, ty: float) -> 'Matrix3x3':
        """Crée une matrice de translation"""
        return cls([
            [1.0, 0.0, tx],
            [0.0, 1.0, ty],
            [0.0, 0.0, 1.0]
        ])
    
    @classmethod
    def rotation(cls, angle: float, center: Point = None) -> 'Matrix3x3':
        """
        Crée une matrice de rotation
        
        Args:
            angle: Angle en radians (sens anti-horaire positif)
            center: Centre de rotation (origine si None)
        """
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        if center is None or (center.x == 0 and center.y == 0):
            return cls([
                [cos_a, -sin_a, 0.0],
                [sin_a, cos_a, 0.0],
                [0.0, 0.0, 1.0]
            ])
        else:
            # Translation au centre, rotation, translation inverse
            cx, cy = center.x, center.y
            return cls([
                [cos_a, -sin_a, cx - cos_a * cx + sin_a * cy],
                [sin_a, cos_a, cy - sin_a * cx - cos_a * cy],
                [0.0, 0.0, 1.0]
            ])
    
    @classmethod
    def scaling(cls, sx: float, sy: float, center: Point = None) -> 'Matrix3x3':
        """
        Crée une matrice de mise à l'échelle
        
        Args:
            sx, sy: Facteurs d'échelle
            center: Centre de mise à l'échelle (origine si None)
        """
        if center is None or (center.x == 0 and center.y == 0):
            return cls([
                [sx, 0.0, 0.0],
                [0.0, sy, 0.0],
                [0.0, 0.0, 1.0]
            ])
        else:
            cx, cy = center.x, center.y
            return cls([
                [sx, 0.0, cx * (1 - sx)],
                [0.0, sy, cy * (1 - sy)],
                [0.0, 0.0, 1.0]
            ])
    
    @classmethod
    def shearing(cls, shx: float, shy: float) -> 'Matrix3x3':
        """
        Crée une matrice de cisaillement
        
        Args:
            shx: Cisaillement horizontal
            shy: Cisaillement vertical
        """
        return cls([
            [1.0, shx, 0.0],
            [shy, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
    
    @classmethod
    def reflection_x(cls) -> 'Matrix3x3':
        """Crée une matrice de réflexion par rapport à l'axe X"""
        return cls([
            [1.0, 0.0, 0.0],
            [0.0, -1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
    
    @classmethod
    def reflection_y(cls) -> 'Matrix3x3':
        """Crée une matrice de réflexion par rapport à l'axe Y"""
        return cls([
            [-1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0]
        ])
    
    def __mul__(self, other: 'Matrix3x3') -> 'Matrix3x3':
        """Multiplication de matrices"""
        result = [[0.0] * 3 for _ in range(3)]
        
        for i in range(3):
            for j in range(3):
                for k in range(3):
                    result[i][j] += self.m[i][k] * other.m[k][j]
        
        return Matrix3x3(result)
    
    def transform_point(self, point: Point) -> Point:
        """Applique la transformation à un point"""
        x = self.m[0][0] * point.x + self.m[0][1] * point.y + self.m[0][2]
        y = self.m[1][0] * point.x + self.m[1][1] * point.y + self.m[1][2]
        w = self.m[2][0] * point.x + self.m[2][1] * point.y + self.m[2][2]
        
        if w != 0 and w != 1:
            x /= w
            y /= w
        
        return Point(x, y)
    
    def transform_points(self, points: List[Point]) -> List[Point]:
        """Applique la transformation à une liste de points"""
        return [self.transform_point(p) for p in points]
    
    def determinant(self) -> float:
        """Calcule le déterminant de la matrice"""
        return (
            self.m[0][0] * (self.m[1][1] * self.m[2][2] - self.m[1][2] * self.m[2][1]) -
            self.m[0][1] * (self.m[1][0] * self.m[2][2] - self.m[1][2] * self.m[2][0]) +
            self.m[0][2] * (self.m[1][0] * self.m[2][1] - self.m[1][1] * self.m[2][0])
        )
    
    def inverse(self) -> Optional['Matrix3x3']:
        """Calcule l'inverse de la matrice (si elle existe)"""
        det = self.determinant()
        
        if abs(det) < 1e-10:
            return None
        
        inv_det = 1.0 / det
        
        result = [
            [
                (self.m[1][1] * self.m[2][2] - self.m[1][2] * self.m[2][1]) * inv_det,
                (self.m[0][2] * self.m[2][1] - self.m[0][1] * self.m[2][2]) * inv_det,
                (self.m[0][1] * self.m[1][2] - self.m[0][2] * self.m[1][1]) * inv_det
            ],
            [
                (self.m[1][2] * self.m[2][0] - self.m[1][0] * self.m[2][2]) * inv_det,
                (self.m[0][0] * self.m[2][2] - self.m[0][2] * self.m[2][0]) * inv_det,
                (self.m[0][2] * self.m[1][0] - self.m[0][0] * self.m[1][2]) * inv_det
            ],
            [
                (self.m[1][0] * self.m[2][1] - self.m[1][1] * self.m[2][0]) * inv_det,
                (self.m[0][1] * self.m[2][0] - self.m[0][0] * self.m[2][1]) * inv_det,
                (self.m[0][0] * self.m[1][1] - self.m[0][1] * self.m[1][0]) * inv_det
            ]
        ]
        
        return Matrix3x3(result)
    
    def transpose(self) -> 'Matrix3x3':
        """Retourne la transposée de la matrice"""
        result = [[self.m[j][i] for j in range(3)] for i in range(3)]
        return Matrix3x3(result)
    
    def __repr__(self) -> str:
        rows = []
        for row in self.m:
            rows.append(f"  [{row[0]:8.3f}, {row[1]:8.3f}, {row[2]:8.3f}]")
        return "Matrix3x3(\n" + "\n".join(rows) + "\n)"


class TransformBuilder:
    """
    Builder pour créer des transformations composées
    Permet d'enchaîner les transformations de manière fluide
    """
    
    def __init__(self):
        self.matrix = Matrix3x3.identity()
    
    def translate(self, tx: float, ty: float) -> 'TransformBuilder':
        """Ajoute une translation"""
        self.matrix = Matrix3x3.translation(tx, ty) * self.matrix
        return self
    
    def rotate(self, angle: float, center: Point = None) -> 'TransformBuilder':
        """Ajoute une rotation (angle en radians)"""
        self.matrix = Matrix3x3.rotation(angle, center) * self.matrix
        return self
    
    def rotate_degrees(self, angle: float, center: Point = None) -> 'TransformBuilder':
        """Ajoute une rotation (angle en degrés)"""
        return self.rotate(math.radians(angle), center)
    
    def scale(self, sx: float, sy: float = None, center: Point = None) -> 'TransformBuilder':
        """Ajoute une mise à l'échelle"""
        if sy is None:
            sy = sx
        self.matrix = Matrix3x3.scaling(sx, sy, center) * self.matrix
        return self
    
    def shear(self, shx: float, shy: float) -> 'TransformBuilder':
        """Ajoute un cisaillement"""
        self.matrix = Matrix3x3.shearing(shx, shy) * self.matrix
        return self
    
    def reflect_x(self) -> 'TransformBuilder':
        """Ajoute une réflexion par rapport à X"""
        self.matrix = Matrix3x3.reflection_x() * self.matrix
        return self
    
    def reflect_y(self) -> 'TransformBuilder':
        """Ajoute une réflexion par rapport à Y"""
        self.matrix = Matrix3x3.reflection_y() * self.matrix
        return self
    
    def build(self) -> Matrix3x3:
        """Retourne la matrice de transformation finale"""
        return self.matrix
    
    def apply(self, points: List[Point]) -> List[Point]:
        """Applique la transformation à une liste de points"""
        return self.matrix.transform_points(points)
    
    def reset(self) -> 'TransformBuilder':
        """Réinitialise à l'identité"""
        self.matrix = Matrix3x3.identity()
        return self