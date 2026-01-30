"""
Page Matrix - Démonstration des transformations géométriques
Permet de visualiser les effets des matrices de transformation
"""

import pygame
import math
from typing import List, Tuple
from .base_page import BasePage
from ..colors import ColorPalette
from ..page_types import PageType, TransformType
from ..components.button import BackButton
from ...core.point import Point
from ...core.polygon import Polygon
from ...utils.math_utils import Matrix3x3, TransformBuilder


class TransformControl:
    """Contrôle pour ajuster une valeur de transformation"""
    
    def __init__(self, label: str, x: int, y: int, min_val: float, max_val: float, 
                 default_val: float, step: float = 1.0):
        self.label = label
        self.x = x
        self.y = y
        self.min_val = min_val
        self.max_val = max_val
        self.value = default_val
        self.default_val = default_val
        self.step = step
        
        self.width = 200
        self.height = 40
        
        self.slider_rect = pygame.Rect(x + 100, y + 10, 150, 20)
        self.is_dragging = False
        
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gère les événements"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.slider_rect.collidepoint(event.pos):
                self.is_dragging = True
                self._update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self._update_value(event.pos[0])
                return True
        return False
    
    def _update_value(self, mouse_x: int):
        """Met à jour la valeur en fonction de la position de la souris"""
        ratio = (mouse_x - self.slider_rect.left) / self.slider_rect.width
        ratio = max(0, min(1, ratio))
        self.value = self.min_val + ratio * (self.max_val - self.min_val)
    
    def reset(self):
        """Réinitialise à la valeur par défaut"""
        self.value = self.default_val
    
    def draw(self, surface: pygame.Surface):
        """Dessine le contrôle"""
        # Label
        label_text = self.font.render(f"{self.label}:", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        surface.blit(label_text, (self.x, self.y + 10))
        
        # Fond du slider
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_BORDER.rgb, self.slider_rect, border_radius=10)
        
        # Barre de progression
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        fill_width = int(self.slider_rect.width * ratio)
        fill_rect = pygame.Rect(self.slider_rect.x, self.slider_rect.y, fill_width, self.slider_rect.height)
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_ORANGE.rgb, fill_rect, border_radius=10)
        
        # Curseur
        cursor_x = self.slider_rect.x + fill_width
        cursor_rect = pygame.Rect(cursor_x - 5, self.slider_rect.y - 3, 10, self.slider_rect.height + 6)
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_TEXT.rgb, cursor_rect, border_radius=5)
        
        # Valeur
        value_text = self.font.render(f"{self.value:.1f}", True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        surface.blit(value_text, (self.slider_rect.right + 10, self.y + 10))


class MatrixPage(BasePage):
    """Page de démonstration des transformations matricielles"""
    
    def __init__(self, screen: pygame.Surface, app):
        super().__init__(screen, app)
        self.back_button = BackButton(30, 30)
        
        # Polygone de démonstration (maison)
        self.original_polygon = self._create_demo_polygon()
        self.transformed_polygon = self.original_polygon.copy()
        
        # Contrôles de transformation
        self.controls: List[TransformControl] = []
        self._setup_controls()
        
        # Centre de transformation
        self.transform_center = self.original_polygon.get_center()
        
        # Affichage
        self.show_original = True
        self.show_grid = True
        self.show_matrix = True
        
        # Canvas
        self.canvas_rect = pygame.Rect(0, 0, 0, 0)
        self.canvas_center = Point(0, 0)
    
    def _create_demo_polygon(self) -> Polygon:
        """Crée un polygone de démonstration (forme de maison)"""
        # Coordonnées relatives au centre
        vertices = [
            Point(-50, 50),   # Bas gauche
            Point(50, 50),    # Bas droite
            Point(50, -20),   # Haut droite du corps
            Point(0, -70),    # Pointe du toit
            Point(-50, -20),  # Haut gauche du corps
        ]
        
        poly = Polygon(vertices, "Maison")
        poly.color = ColorPalette.POLYGON_DEFAULT.rgb
        return poly
    
    def _setup_controls(self):
        """Configure les contrôles de transformation"""
        x = 50
        y = 250
        spacing = 50
        
        # Translation
        self.controls.append(TransformControl("Trans. X", x, y, -200, 200, 0, 10))
        self.controls.append(TransformControl("Trans. Y", x, y + spacing, -200, 200, 0, 10))
        
        # Rotation
        self.controls.append(TransformControl("Rotation", x, y + spacing * 2, -180, 180, 0, 5))
        
        # Échelle
        self.controls.append(TransformControl("Échelle X", x, y + spacing * 3, 0.1, 3, 1, 0.1))
        self.controls.append(TransformControl("Échelle Y", x, y + spacing * 4, 0.1, 3, 1, 0.1))
        
        # Cisaillement
        self.controls.append(TransformControl("Cisail. X", x, y + spacing * 5, -1, 1, 0, 0.1))
        self.controls.append(TransformControl("Cisail. Y", x, y + spacing * 6, -1, 1, 0, 0.1))
    
    def _apply_transformations(self):
        """Applique les transformations au polygone"""
        # Récupérer les valeurs
        tx = self.controls[0].value
        ty = self.controls[1].value
        rotation = math.radians(self.controls[2].value)
        sx = self.controls[3].value
        sy = self.controls[4].value
        shx = self.controls[5].value
        shy = self.controls[6].value
        
        # Construire la transformation
        builder = TransformBuilder()
        
        # Ordre: Cisaillement -> Échelle -> Rotation -> Translation
        # (appliqué dans l'ordre inverse car on multiplie à gauche)
        center = self.transform_center
        
        if shx != 0 or shy != 0:
            builder.shear(shx, shy)
        
        if sx != 1 or sy != 1:
            builder.scale(sx, sy, center)
        
        if rotation != 0:
            builder.rotate(rotation, center)
        
        if tx != 0 or ty != 0:
            builder.translate(tx, ty)
        
        # Appliquer la transformation
        transformed_vertices = builder.apply(self.original_polygon.vertices)
        
        self.transformed_polygon = Polygon(transformed_vertices, "Transformé")
        self.transformed_polygon.color = ColorPalette.MATHEMATICA_ORANGE.rgb
        
        # Stocker la matrice pour affichage
        self.current_matrix = builder.build()
    
    def _reset_transformations(self):
        """Réinitialise toutes les transformations"""
        for control in self.controls:
            control.reset()
        self._apply_transformations()
    
    def handle_event(self, event: pygame.event.Event):
        """Gère les événements"""
        if self.back_button.handle_event(event):
            self.app.navigate_to(PageType.HOME)
            return
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.app.navigate_to(PageType.HOME)
            elif event.key == pygame.K_r:
                self._reset_transformations()
            elif event.key == pygame.K_o:
                self.show_original = not self.show_original
            elif event.key == pygame.K_g:
                self.show_grid = not self.show_grid
            elif event.key == pygame.K_m:
                self.show_matrix = not self.show_matrix
        
        # Contrôles
        for control in self.controls:
            if control.handle_event(event):
                self._apply_transformations()
    
    def update(self):
        """Mise à jour"""
        pass
    
    def draw(self):
        """Dessine la page"""
        # Bouton retour
        self.back_button.draw(self.screen)
        
        # Titre
        title = self.font_title.render("Transformations Matricielles", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 50))
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.font_normal.render("Visualisation des matrices 2D homogènes", True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 90))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Panel des contrôles
        control_panel = pygame.Rect(30, 200, 320, 420)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_CARD.rgb, control_panel, border_radius=12)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_BORDER.rgb, control_panel, 2, border_radius=12)
        
        # Titre du panel
        panel_title = self.font_normal.render("Paramètres", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        self.screen.blit(panel_title, (50, 210))
        
        # Dessiner les contrôles
        for control in self.controls:
            control.draw(self.screen)
        
        # Bouton reset
        reset_rect = pygame.Rect(100, 610, 150, 35)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_ORANGE.rgb, reset_rect, border_radius=6)
        reset_text = self.font_small.render("Réinitialiser (R)", True, (255, 255, 255))
        reset_text_rect = reset_text.get_rect(center=reset_rect.center)
        self.screen.blit(reset_text, reset_text_rect)
        
        # Canvas de visualisation
        self.canvas_rect = pygame.Rect(380, 150, 780, 500)
        pygame.draw.rect(self.screen, (255, 255, 255), self.canvas_rect, border_radius=8)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_BORDER.rgb, self.canvas_rect, 2, border_radius=8)
        
        self.canvas_center = Point(
            self.canvas_rect.centerx,
            self.canvas_rect.centery
        )
        
        # Clip au canvas
        self.screen.set_clip(self.canvas_rect)
        
        # Grille
        if self.show_grid:
            self._draw_grid()
        
        # Axes
        self._draw_axes()
        
        # Polygone original (semi-transparent)
        if self.show_original:
            self._draw_polygon(self.original_polygon, alpha=100)
        
        # Polygone transformé
        self._draw_polygon(self.transformed_polygon, alpha=255)
        
        # Centre de transformation
        center_screen = self._world_to_screen(self.transform_center)
        pygame.draw.circle(self.screen, (255, 0, 0), center_screen, 6)
        pygame.draw.circle(self.screen, (255, 255, 255), center_screen, 4)
        
        # Reset clip
        self.screen.set_clip(None)
        
        # Affichage de la matrice
        if self.show_matrix:
            self._draw_matrix_display()
        
        # Instructions
        self._draw_instructions()
    
    def _world_to_screen(self, point: Point) -> Tuple[int, int]:
        """Convertit les coordonnées monde en coordonnées écran"""
        return (
            int(self.canvas_center.x + point.x),
            int(self.canvas_center.y + point.y)
        )
    
    def _draw_grid(self):
        """Dessine la grille"""
        grid_spacing = 50
        grid_color = (230, 230, 230)
        
        # Lignes verticales
        for x in range(self.canvas_rect.left, self.canvas_rect.right, grid_spacing):
            alpha = 150 if (x - int(self.canvas_center.x)) % 100 == 0 else 80
            pygame.draw.line(
                self.screen, 
                (*grid_color[:3],),
                (x, self.canvas_rect.top),
                (x, self.canvas_rect.bottom)
            )
        
        # Lignes horizontales
        for y in range(self.canvas_rect.top, self.canvas_rect.bottom, grid_spacing):
            pygame.draw.line(
                self.screen,
                grid_color,
                (self.canvas_rect.left, y),
                (self.canvas_rect.right, y)
            )
    
    def _draw_axes(self):
        """Dessine les axes X et Y"""
        axis_color = (150, 150, 150)
        
        # Axe X
        pygame.draw.line(
            self.screen, axis_color,
            (self.canvas_rect.left, int(self.canvas_center.y)),
            (self.canvas_rect.right, int(self.canvas_center.y)),
            2
        )
        
        # Axe Y
        pygame.draw.line(
            self.screen, axis_color,
            (int(self.canvas_center.x), self.canvas_rect.top),
            (int(self.canvas_center.x), self.canvas_rect.bottom),
            2
        )
        
        # Labels
        x_label = self.font_small.render("X", True, axis_color)
        self.screen.blit(x_label, (self.canvas_rect.right - 20, int(self.canvas_center.y) + 5))
        
        y_label = self.font_small.render("Y", True, axis_color)
        self.screen.blit(y_label, (int(self.canvas_center.x) + 5, self.canvas_rect.top + 5))
    
    def _draw_polygon(self, polygon: Polygon, alpha: int = 255):
        """Dessine un polygone"""
        if len(polygon.vertices) < 3:
            return
        
        screen_points = [self._world_to_screen(p) for p in polygon.vertices]
        
        # Remplissage semi-transparent
        if alpha < 255:
            s = pygame.Surface((self.canvas_rect.width, self.canvas_rect.height), pygame.SRCALPHA)
            adjusted_points = [(p[0] - self.canvas_rect.x, p[1] - self.canvas_rect.y) for p in screen_points]
            pygame.draw.polygon(s, (*polygon.color, alpha // 2), adjusted_points)
            self.screen.blit(s, self.canvas_rect.topleft)
        
        # Contour
        color = (*polygon.color,) if alpha == 255 else (*polygon.color,)
        pygame.draw.polygon(self.screen, color, screen_points, 3 if alpha == 255 else 1)
        
        # Sommets
        for sp in screen_points:
            pygame.draw.circle(self.screen, polygon.color, sp, 5)
            pygame.draw.circle(self.screen, (255, 255, 255), sp, 3)
    
    def _draw_matrix_display(self):
        """Affiche la matrice de transformation"""
        panel_rect = pygame.Rect(380, 660, 350, 120)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_CARD.rgb, panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_BORDER.rgb, panel_rect, 1, border_radius=8)
        
        # Titre
        title = self.font_small.render("Matrice de transformation:", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        self.screen.blit(title, (390, 670))
        
        # Matrice
        if hasattr(self, 'current_matrix'):
            matrix_font = pygame.font.Font(None, 20)
            y = 695
            for row in self.current_matrix.m:
                row_text = f"[{row[0]:8.3f}  {row[1]:8.3f}  {row[2]:8.3f}]"
                text = matrix_font.render(row_text, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
                self.screen.blit(text, (400, y))
                y += 22
    
    def _draw_instructions(self):
        """Dessine les instructions"""
        instructions = [
            "O: Afficher/masquer original",
            "G: Afficher/masquer grille",
            "M: Afficher/masquer matrice",
            "R: Réinitialiser"
        ]
        
        y = 670
        for instr in instructions:
            text = self.font_small.render(instr, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
            self.screen.blit(text, (750, y))
            y += 25
    
    def on_enter(self):
        """Appelé quand on entre dans la page"""
        self._apply_transformations()