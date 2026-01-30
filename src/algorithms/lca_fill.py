"""
Algorithme LCA (Liste des Côtés Actifs) pour le remplissage de polygones
Principe SOLID: Single Responsibility - gère uniquement le remplissage
"""

from typing import List, Tuple
import math
from src.core.point import Point
from src.core.polygon import Polygon


class EdgeEntry:
    """Entrée dans la liste des côtés actifs"""
    def __init__(self, y_max: float, x_min: float, inv_slope: float):
        self.y_max = y_max
        self.x_current = x_min
        self.inv_slope = inv_slope

    def __repr__(self):
        return f"Edge(y_max={self.y_max}, x={self.x_current:.2f}, 1/m={self.inv_slope:.2f})"


class LCAFill:
    """Implémentation de l'algorithme LCA pour le remplissage"""

    def __init__(self):
        self.active_edge_table: List[EdgeEntry] = []
        self.scan_line_table: List[List[EdgeEntry]] = []
        self._y_min_global: int = 0
        self._y_max_global: int = 0

    def fill_polygon(self, polygon: Polygon) -> List[Tuple[Point, Point]]:
        """
        Remplit un polygone et retourne la liste des segments à dessiner
        Returns: Liste de segments (Point début, Point fin)
        """
        if polygon is None or len(polygon.vertices) < 3:
            return []

        self._build_scan_line_table(polygon)

        segments: List[Tuple[Point, Point]] = []
        self.active_edge_table.clear()

        # Balayage : y in [y_min_global, y_max_global)
        for y in range(self._y_min_global, self._y_max_global):
            self._update_active_edges(y)
            segments.extend(self._get_fill_segments(y))

            # Mise à jour des intersections pour la ligne suivante
            for e in self.active_edge_table:
                e.x_current += e.inv_slope

        return segments

    def _build_scan_line_table(self, polygon: Polygon):
        """
        Construit la Structure Intermédiaire (SI) indexée par y (entier).
        Pour chaque arête non horizontale :
          - calcule y_max, x(y_min), inv_slope
          - range dans SI[y_min]
        """
        min_p, max_p = polygon.get_bounding_box()
        self._y_min_global = int(math.floor(min_p.y))
        self._y_max_global = int(math.ceil(max_p.y))

        # Table SI de taille suffisante (indexation absolue en y)
        size = max(0, self._y_max_global + 1)
        self.scan_line_table = [[] for _ in range(size)]

        for p1, p2 in polygon.get_edges():
            # ignorer horizontales
            if p1.y == p2.y:
                continue

            # ordonner du bas vers le haut
            if p1.y < p2.y:
                y_min = p1.y
                y_max = p2.y
                x_at_ymin = p1.x
                dx = p2.x - p1.x
                dy = p2.y - p1.y
            else:
                y_min = p2.y
                y_max = p1.y
                x_at_ymin = p2.x
                dx = p1.x - p2.x
                dy = p1.y - p2.y

            inv_slope = dx / dy  # 1/m

            # Convention classique : actif pour y in [ceil(y_min), ceil(y_max))
            y_start = int(math.ceil(y_min))
            y_end_excl = int(math.ceil(y_max))  # retire à y >= y_end_excl

            if y_start < self._y_min_global:
                # décaler x_at_ymin jusqu'à y_start
                x_at_ymin += (y_start - y_min) * inv_slope
            if y_start >= y_end_excl:
                continue

            entry = EdgeEntry(y_max=y_end_excl, x_min=x_at_ymin, inv_slope=inv_slope)

            if 0 <= y_start < len(self.scan_line_table):
                self.scan_line_table[y_start].append(entry)

    def _update_active_edges(self, y: int):
        """
        Met à jour la LCA pour la ligne y :
          - ajoute SI[y]
          - retire arêtes finies (y >= y_max)
          - trie par x_current
        """
        # Ajouter les arêtes qui commencent à y
        if 0 <= y < len(self.scan_line_table):
            self.active_edge_table.extend(self.scan_line_table[y])

        # Retirer celles qui finissent à y (y >= y_max_excl)
        self.active_edge_table = [e for e in self.active_edge_table if y < e.y_max]

        # Trier par abscisse d'intersection
        self.active_edge_table.sort(key=lambda e: e.x_current)

    def _get_fill_segments(self, y: int) -> List[Tuple[Point, Point]]:
        """
        Calcule les segments à dessiner pour la ligne y (règle pair/impair).
        """
        segs: List[Tuple[Point, Point]] = []
        n = len(self.active_edge_table)
        if n < 2:
            return segs

        # prendre les intersections par paires
        for i in range(0, n - 1, 2):
            x1 = self.active_edge_table[i].x_current
            x2 = self.active_edge_table[i + 1].x_current
            if x1 > x2:
                x1, x2 = x2, x1

            # arrondis pour "remplir à l'intérieur"
            xs = int(math.ceil(x1))
            xe = int(math.floor(x2))

            if xs <= xe:
                segs.append((Point(xs, y), Point(xe, y)))

        return segs
