"""
Algorithme de Sutherland-Hodgman pour le fenêtrage de polygones
Principe SOLID: Single Responsibility - gère uniquement le clipping
"""

from typing import List
from src.core.point import Point
from src.core.polygon import Polygon

class SutherlandHodgman:
    
    def __init__(self, clip_window: Polygon = None):
        self.clip_window = clip_window

    def clip_polygon(self, subject: Polygon, clip_window: Polygon = None) -> Polygon:
        """
        Clippe le polygone sujet par la fenêtre de clipping.
        Si clip_window est fourni, il est utilisé. Sinon, on utilise self.clip_window.
        """
        window_to_use = clip_window if clip_window is not None else self.clip_window
        
        if window_to_use is None:
            print("Erreur: Aucune fenêtre de clipping définie.")
            return subject

        PL = subject.vertices # std::vector<Point> PL
        
        windows = self._ensure_clockwise(window_to_use.vertices)
        
        PS = [] # std::vector<Point> PS 

        N3 = len(windows)
        
        if N3 < 3:
            return subject

        for i in range(N3):
            
            A = windows[i]
            B = windows[(i + 1) % N3]
            
            # On vide la liste de sortie pour ce tour
            PS = [] 
            
            # N1 : Taille du polygone actuel
            N1 = len(PL)
            
            F = None 
            S = None 
            P = None 

            for j in range(N1):
                
                P = PL[j] # 
                
                if j == 0:
                    F = P 
                    S = P 
                else:
                    # Si l'un est dedans et l'autre dehors -> Ça coupe
                    if self.visible(S, A, B) != self.visible(P, A, B):
                        I = self.intersection(S, P, A, B)
                        PS.append(I)
                S = P
                if self.visible(S, A, B):
                    PS.append(S)

            if len(PS) > 0:
                if self.visible(S, A, B) != self.visible(F, A, B):
                    I = self.intersection(S, F, A, B)
                    PS.append(I)
            PL = PS # Le résultat devient l'entrée suivante
        return Polygon(PL)

    def _ensure_clockwise(self, vertices: List[Point]) -> List[Point]:
        """
        Vérifie et corrige l'ordre des sommets pour qu'ils soient dans le sens horaire (Clockwise).
        """
        if len(vertices) < 3:
            return vertices
            
        # Calcul de l'aire signée
        area = 0.0
        for i in range(len(vertices)):
            j = (i + 1) % len(vertices)
            area += (vertices[j].x - vertices[i].x) * (vertices[j].y + vertices[i].y)
        
        if area > 0: 
             return vertices[::-1] # On inverse
        return vertices

    def visible(self, P: Point, A: Point, B: Point) -> bool:
        """
        Est-ce que P est visible (Dedans) par rapport au bord A->B 
        """
        # Vecteur du bord
        dx_bord = B.x - A.x
        dy_bord = B.y - A.y
        
        # Vecteur vers le point
        dx_point = P.x - A.x
        dy_point = P.y - A.y
        
        # Produit en croix
        cross_product = (dx_bord * dy_point) - (dy_bord * dx_point)
        
        return cross_product >= 0
    
    def intersection(self, S: Point, P: Point, A: Point, B: Point) -> Point:
        """
        Calcule le point I intersection entre [S,P] et [A,B]
        """
        # Vecteurs
        x1, y1 = S.x, S.y
        x2, y2 = P.x, P.y
        x3, y3 = A.x, A.y
        x4, y4 = B.x, B.y
        
        # Dénominateur
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if denom == 0:
            return S # Fallback safe
            
        # Calcul de t
        t_num = (x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)
        t = t_num / denom
        
        # Point final I
        ix = x1 + t * (x2 - x1)
        iy = y1 + t * (y2 - y1)
        
        return Point(ix, iy)
