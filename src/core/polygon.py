"""
Module Polygon - Représentation d'un polygone
Principe SOLID: Single Responsibility - gère uniquement les polygones
Version améliorée avec plus de fonctionnalités
"""

from typing import List, Tuple, Optional
from .point import Point
import json


class Polygon:
    """
    Représentation d'un polygone défini par une liste de sommets
    """
    
    _id_counter = 0  # Compteur global pour les IDs uniques
    
    def __init__(self, vertices: List[Point] = None, name: str = None):
        """
        Initialise un polygone
        
        Args:
            vertices: Liste des sommets du polygone
            name: Nom optionnel du polygone
        """
        Polygon._id_counter += 1
        self.id = Polygon._id_counter
        self.vertices = vertices if vertices is not None else []
        self.name = name if name else f"Polygone {self.id}"
        self.color = (100, 149, 237)  # Bleu par défaut
        self.fill_color = (100, 149, 237, 128)  # Couleur de remplissage avec alpha
        self.is_selected = False
        self.is_visible = True
        self.is_locked = False  # Empêche les modifications
        self.line_width = 2
        self.selected_vertex_index: Optional[int] = None
    
    def add_vertex(self, point: Point, index: int = None):
        """
        Ajoute un sommet au polygone
        
        Args:
            point: Le point à ajouter
            index: Position d'insertion (fin si None)
        """
        if self.is_locked:
            return
        if index is None:
            self.vertices.append(point)
        else:
            self.vertices.insert(index, point)
    
    def remove_vertex(self, index: int) -> Optional[Point]:
        """
        Supprime un sommet par son index
        
        Returns:
            Le point supprimé ou None
        """
        if self.is_locked or index < 0 or index >= len(self.vertices):
            return None
        return self.vertices.pop(index)
    
    def move_vertex(self, index: int, new_position: Point):
        """Déplace un sommet à une nouvelle position"""
        if self.is_locked or index < 0 or index >= len(self.vertices):
            return
        self.vertices[index] = new_position
    
    def clear(self):
        """Vide le polygone"""
        if not self.is_locked:
            self.vertices.clear()
            self.selected_vertex_index = None
    
    def is_empty(self) -> bool:
        """Vérifie si le polygone est vide"""
        return len(self.vertices) == 0
    
    def is_closed(self) -> bool:
        """Vérifie si le polygone a au moins 3 sommets"""
        return len(self.vertices) >= 3
    
    def get_edges(self) -> List[Tuple[Point, Point]]:
        """
        Retourne la liste des arêtes du polygone
        Une arête = (Point début, Point fin)
        """
        if len(self.vertices) < 2:
            return []
        
        edges = []
        for i in range(len(self.vertices)):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % len(self.vertices)]
            edges.append((p1, p2))
        
        return edges
    
    def is_convex(self) -> bool:
        """
        Vérifie si le polygone est convexe
        Un polygone est convexe si tous les produits vectoriels ont le même signe
        """
        if len(self.vertices) < 3:
            return False
        
        sign = None
        n = len(self.vertices)
        
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            p3 = self.vertices[(i + 2) % n]
            
            # Vecteurs
            v1 = p2 - p1
            v2 = p3 - p2
            
            # Produit vectoriel
            cross = v1.cross(v2)
            
            if cross != 0:
                if sign is None:
                    sign = cross > 0
                elif (cross > 0) != sign:
                    return False
        
        return True
    
    def get_bounding_box(self) -> Tuple[Point, Point]:
        """
        Retourne le rectangle englobant (bounding box)
        Returns: (Point min, Point max)
        """
        if self.is_empty():
            return Point(0, 0), Point(0, 0)
        
        min_x = min(p.x for p in self.vertices)
        max_x = max(p.x for p in self.vertices)
        min_y = min(p.y for p in self.vertices)
        max_y = max(p.y for p in self.vertices)
        
        return Point(min_x, min_y), Point(max_x, max_y)
    
    def get_center(self) -> Point:
        """Retourne le centre (centroïde) du polygone"""
        if self.is_empty():
            return Point(0, 0)
        
        cx = sum(p.x for p in self.vertices) / len(self.vertices)
        cy = sum(p.y for p in self.vertices) / len(self.vertices)
        return Point(cx, cy)
    
    def get_area(self) -> float:
        """Calcule l'aire du polygone (formule du lacet)"""
        if len(self.vertices) < 3:
            return 0.0
        
        area = 0.0
        n = len(self.vertices)
        
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y
        
        return abs(area) / 2.0
    
    def get_perimeter(self) -> float:
        """Calcule le périmètre du polygone"""
        if len(self.vertices) < 2:
            return 0.0
        
        perimeter = 0.0
        for p1, p2 in self.get_edges():
            perimeter += p1.distance_to(p2)
        
        return perimeter
    
    def contains_point(self, point: Point) -> bool:
        """
        Vérifie si un point est à l'intérieur du polygone
        Utilise la méthode du raycasting (nombre d'intersections impair)
        """
        if len(self.vertices) < 3:
            return False
        
        n = len(self.vertices)
        inside = False
        
        j = n - 1
        for i in range(n):
            xi, yi = self.vertices[i].x, self.vertices[i].y
            xj, yj = self.vertices[j].x, self.vertices[j].y
            
            if ((yi > point.y) != (yj > point.y)) and \
               (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi):
                inside = not inside
            
            j = i
        
        return inside
    
    def find_vertex_at(self, point: Point, threshold: float = 10.0) -> Optional[int]:
        """
        Trouve l'index du sommet le plus proche d'un point
        
        Args:
            point: Point de recherche
            threshold: Distance maximale pour considérer un match
            
        Returns:
            Index du sommet ou None
        """
        for i, vertex in enumerate(self.vertices):
            if vertex.distance_to(point) <= threshold:
                return i
        return None
    
    def find_edge_at(self, point: Point, threshold: float = 10.0) -> Optional[int]:
        """
        Trouve l'index de l'arête la plus proche d'un point
        
        Returns:
            Index de l'arête (index du premier point) ou None
        """
        if len(self.vertices) < 2:
            return None
        
        for i, (p1, p2) in enumerate(self.get_edges()):
            dist = self._point_to_segment_distance(point, p1, p2)
            if dist <= threshold:
                return i
        return None
    
    def _point_to_segment_distance(self, point: Point, p1: Point, p2: Point) -> float:
        """Calcule la distance d'un point à un segment"""
        # Vecteur du segment
        segment = p2 - p1
        segment_length_sq = segment.x * segment.x + segment.y * segment.y
        
        if segment_length_sq == 0:
            return point.distance_to(p1)
        
        # Projection du point sur la ligne
        t = max(0, min(1, ((point.x - p1.x) * segment.x + (point.y - p1.y) * segment.y) / segment_length_sq))
        
        # Point le plus proche sur le segment
        closest = Point(p1.x + t * segment.x, p1.y + t * segment.y)
        
        return point.distance_to(closest)
    
    def translate(self, dx: float, dy: float):
        """Translate le polygone"""
        if self.is_locked:
            return
        for i in range(len(self.vertices)):
            self.vertices[i] = Point(self.vertices[i].x + dx, self.vertices[i].y + dy)
    
    def scale(self, sx: float, sy: float, center: Point = None):
        """
        Met à l'échelle le polygone
        
        Args:
            sx, sy: Facteurs d'échelle
            center: Centre de mise à l'échelle (centre du polygone si None)
        """
        if self.is_locked:
            return
        if center is None:
            center = self.get_center()
        
        for i in range(len(self.vertices)):
            p = self.vertices[i]
            self.vertices[i] = Point(
                center.x + (p.x - center.x) * sx,
                center.y + (p.y - center.y) * sy
            )
    
    def rotate(self, angle: float, center: Point = None):
        """
        Fait pivoter le polygone
        
        Args:
            angle: Angle en radians
            center: Centre de rotation (centre du polygone si None)
        """
        import math
        if self.is_locked:
            return
        if center is None:
            center = self.get_center()
        
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        for i in range(len(self.vertices)):
            p = self.vertices[i]
            dx = p.x - center.x
            dy = p.y - center.y
            self.vertices[i] = Point(
                center.x + dx * cos_a - dy * sin_a,
                center.y + dx * sin_a + dy * cos_a
            )
    
    def set_color(self, color: Tuple[int, int, int]):
        """Définit la couleur du polygone"""
        self.color = color
    
    def set_fill_color(self, color: Tuple[int, int, int, int]):
        """Définit la couleur de remplissage (avec alpha)"""
        self.fill_color = color
    
    def copy(self) -> 'Polygon':
        """Crée une copie du polygone"""
        new_poly = Polygon([Point(p.x, p.y) for p in self.vertices])
        new_poly.color = self.color
        new_poly.fill_color = self.fill_color
        new_poly.line_width = self.line_width
        new_poly.name = f"{self.name} (copie)"
        return new_poly
    
    def reverse(self):
        """Inverse l'ordre des sommets"""
        if not self.is_locked:
            self.vertices.reverse()
    
    def to_dict(self) -> dict:
        """Convertit le polygone en dictionnaire (pour export)"""
        return {
            'name': self.name,
            'vertices': [(p.x, p.y) for p in self.vertices],
            'color': self.color,
            'fill_color': self.fill_color,
            'line_width': self.line_width,
            'is_visible': self.is_visible,
            'is_locked': self.is_locked
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Polygon':
        """Crée un polygone à partir d'un dictionnaire"""
        vertices = [Point(x, y) for x, y in data.get('vertices', [])]
        poly = cls(vertices, data.get('name'))
        poly.color = tuple(data.get('color', (100, 149, 237)))
        poly.fill_color = tuple(data.get('fill_color', (100, 149, 237, 128)))
        poly.line_width = data.get('line_width', 2)
        poly.is_visible = data.get('is_visible', True)
        poly.is_locked = data.get('is_locked', False)
        return poly
    
    def __len__(self) -> int:
        """Retourne le nombre de sommets"""
        return len(self.vertices)
    
    def __repr__(self) -> str:
        return f"Polygon(id={self.id}, name='{self.name}', {len(self.vertices)} vertices)"


class PolygonManager:
    """
    Gestionnaire de plusieurs polygones
    Implémente le pattern Observer pour notifier des changements
    """
    
    def __init__(self):
        self.polygons: List[Polygon] = []
        self.selected_index: Optional[int] = None
        self.clipping_window: Optional[Polygon] = None
        self._history: List[List[dict]] = []  # Pour undo
        self._history_index: int = -1
        self._max_history: int = 50
    
    def add_polygon(self, polygon: Polygon) -> int:
        """
        Ajoute un polygone et retourne son index
        """
        self._save_state()
        self.polygons.append(polygon)
        return len(self.polygons) - 1
    
    def remove_polygon(self, index: int) -> Optional[Polygon]:
        """Supprime un polygone par son index"""
        if 0 <= index < len(self.polygons):
            self._save_state()
            polygon = self.polygons.pop(index)
            if self.selected_index is not None:
                if self.selected_index == index:
                    self.selected_index = None
                elif self.selected_index > index:
                    self.selected_index -= 1
            return polygon
        return None
    
    def get_polygon(self, index: int) -> Optional[Polygon]:
        """Récupère un polygone par son index"""
        if 0 <= index < len(self.polygons):
            return self.polygons[index]
        return None
    
    def get_selected(self) -> Optional[Polygon]:
        """Récupère le polygone sélectionné"""
        if self.selected_index is not None:
            return self.get_polygon(self.selected_index)
        return None
    
    def select(self, index: Optional[int]):
        """Sélectionne un polygone"""
        # Désélectionner l'ancien
        if self.selected_index is not None and self.selected_index < len(self.polygons):
            self.polygons[self.selected_index].is_selected = False
        
        # Sélectionner le nouveau
        if index is not None and 0 <= index < len(self.polygons):
            self.selected_index = index
            self.polygons[index].is_selected = True
        else:
            self.selected_index = None
    
    def select_at_point(self, point: Point) -> Optional[int]:
        """
        Sélectionne le polygone contenant le point
        Priorité aux polygones au-dessus (derniers ajoutés)
        """
        for i in range(len(self.polygons) - 1, -1, -1):
            poly = self.polygons[i]
            if poly.is_visible and poly.contains_point(point):
                self.select(i)
                return i
        return None
    
    def find_vertex_at(self, point: Point, threshold: float = 10.0) -> Optional[Tuple[int, int]]:
        """
        Trouve un sommet à une position
        
        Returns:
            (polygon_index, vertex_index) ou None
        """
        for i in range(len(self.polygons) - 1, -1, -1):
            poly = self.polygons[i]
            if poly.is_visible and not poly.is_locked:
                vertex_idx = poly.find_vertex_at(point, threshold)
                if vertex_idx is not None:
                    return (i, vertex_idx)
        return None
    
    def clear(self):
        """Supprime tous les polygones"""
        self._save_state()
        self.polygons.clear()
        self.selected_index = None
        self.clipping_window = None
    
    def set_clipping_window(self, polygon: Polygon):
        """Définit la fenêtre de clipping"""
        self.clipping_window = polygon
    
    def move_up(self, index: int):
        """Monte un polygone d'un niveau (z-order)"""
        if 0 <= index < len(self.polygons) - 1:
            self._save_state()
            self.polygons[index], self.polygons[index + 1] = \
                self.polygons[index + 1], self.polygons[index]
            if self.selected_index == index:
                self.selected_index = index + 1
            elif self.selected_index == index + 1:
                self.selected_index = index
    
    def move_down(self, index: int):
        """Descend un polygone d'un niveau (z-order)"""
        if 0 < index < len(self.polygons):
            self._save_state()
            self.polygons[index], self.polygons[index - 1] = \
                self.polygons[index - 1], self.polygons[index]
            if self.selected_index == index:
                self.selected_index = index - 1
            elif self.selected_index == index - 1:
                self.selected_index = index
    
    def _save_state(self):
        """Sauvegarde l'état actuel pour undo"""
        # Supprimer les états après l'index actuel (si on a fait des undo)
        if self._history_index < len(self._history) - 1:
            self._history = self._history[:self._history_index + 1]
        
        # Sauvegarder l'état
        state = [p.to_dict() for p in self.polygons]
        self._history.append(state)
        self._history_index = len(self._history) - 1
        
        # Limiter la taille de l'historique
        if len(self._history) > self._max_history:
            self._history.pop(0)
            self._history_index -= 1
    
    def undo(self) -> bool:
        """Annule la dernière action"""
        if self._history_index > 0:
            self._history_index -= 1
            self._restore_state(self._history[self._history_index])
            return True
        return False
    
    def redo(self) -> bool:
        """Refait la dernière action annulée"""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self._restore_state(self._history[self._history_index])
            return True
        return False
    
    def _restore_state(self, state: List[dict]):
        """Restaure un état"""
        self.polygons = [Polygon.from_dict(d) for d in state]
        if self.selected_index is not None and self.selected_index >= len(self.polygons):
            self.selected_index = None
    
    def to_json(self) -> str:
        """Exporte tous les polygones en JSON"""
        data = {
            'polygons': [p.to_dict() for p in self.polygons],
            'clipping_window': self.clipping_window.to_dict() if self.clipping_window else None
        }
        return json.dumps(data, indent=2)
    
    def from_json(self, json_str: str):
        """Importe des polygones depuis JSON"""
        self._save_state()
        data = json.loads(json_str)
        self.polygons = [Polygon.from_dict(d) for d in data.get('polygons', [])]
        if data.get('clipping_window'):
            self.clipping_window = Polygon.from_dict(data['clipping_window'])
        self.selected_index = None
    
    def __len__(self) -> int:
        return len(self.polygons)
    
    def __iter__(self):
        return iter(self.polygons)