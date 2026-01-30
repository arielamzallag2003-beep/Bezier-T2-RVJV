"""
Espace de travail pour les polygones - Version améliorée
Supporte plusieurs polygones, drag & drop, transformations, etc.
"""

import pygame
import math
import os
from enum import Enum, auto
from typing import Optional, Tuple, List
from .base_page import BasePage
from ..colors import ColorPalette
from ..page_types import PageType
from ..components.button import BackButton
from ..components.sidebar import Sidebar, ToolButton
from ...core.point import Point
from ...core.polygon import Polygon, PolygonManager
from ...algorithms.sutherland_hodgman import SutherlandHodgman
from ...algorithms.lca_fill import LCAFill


class EditMode(Enum):
    """Modes d'édition disponibles"""
    DRAW_POLYGON = auto()      # Dessiner un nouveau polygone
    DRAW_WINDOW = auto()       # Dessiner la fenêtre de clipping
    SELECT = auto()            # Sélectionner/déplacer des polygones
    EDIT_VERTICES = auto()     # Éditer les sommets
    PAN = auto()               # Déplacer la vue


class PolygonWorkspace(BasePage):
    """
    Espace de travail principal pour la manipulation de polygones
    """
    
    def __init__(self, screen: pygame.Surface, app):
        super().__init__(screen, app)
        
        # Bouton retour
        self.back_button = BackButton(30, 30)
        
        # Sidebar
        self.sidebar = Sidebar(width=320, collapsed_width=50)
        self.sidebar.on_option_change = self._on_option_change
        self._setup_sidebar()
        
        # Boutons outils
        self.tool_buttons: List[ToolButton] = []
        self._setup_tool_buttons()
        
        # Gestionnaire de polygones
        self.polygon_manager = PolygonManager()
        
        # Points en cours de dessin
        self.current_points: List[Point] = []
        
        # Mode d'édition actuel
        self.edit_mode = EditMode.DRAW_POLYGON
        
        # Options d'affichage
        self.show_clipping = False
        self.show_filling = False
        self.show_grid = False
        self.show_vertices = True
        self.show_labels = True
        self.realtime_mode = True
        
        # État de l'interaction
        self.mouse_pos = (0, 0)
        self.is_dragging = False
        self.drag_start: Optional[Point] = None
        self.dragged_vertex: Optional[Tuple[int, int]] = None  # (polygon_idx, vertex_idx)
        self.dragged_polygon_idx: Optional[int] = None
        
        # Zoom et pan
        self.zoom = 1.0
        self.pan_offset = Point(0, 0)
        self.is_panning = False
        self.pan_start: Optional[Point] = None
        
        # Résultats des algorithmes
        self.clipped_polygons: List[Polygon] = []
        self.fill_surface: Optional[pygame.Surface] = None
        
        # Canvas rect (sera calculé dans draw)
        self.canvas_rect = pygame.Rect(0, 0, 0, 0)
        
        # Couleurs des polygones (rotation)
        self.polygon_colors = [
            (65, 105, 225),   # Royal Blue
            (50, 205, 50),    # Lime Green
            (255, 165, 0),    # Orange
            (238, 130, 238),  # Violet
            (0, 206, 209),    # Dark Turquoise
            (255, 99, 71),    # Tomato
            (147, 112, 219),  # Medium Purple
            (60, 179, 113),   # Medium Sea Green
        ]
        self.color_index = 0
        
        # Info texte
        self.status_text = ""
    
    def _setup_sidebar(self):
        """Configure la sidebar avec les sections"""
        # Section Mode
        mode_section = self.sidebar.add_section("Mode")
        mode_section.add_option("Dessiner Polygone", "draw_polygon", True)
        mode_section.add_option("Dessiner Fenetre", "draw_window", False)
        mode_section.add_option("Selection", "select", False)
        mode_section.add_option("Editer Sommets", "edit_vertices", False)
        
        # Section Algorithmes
        algo_section = self.sidebar.add_section("Algorithmes")
        algo_section.add_option("Fenetrage", "clipping", False)
        algo_section.add_option("Remplissage", "filling", False)
        
        # Section Visualisation
        viz_section = self.sidebar.add_section("Visualisation")
        viz_section.add_option("Temps reel", "realtime", True)
        viz_section.add_option("Afficher grille", "grid", False)
        viz_section.add_option("Afficher sommets", "vertices", True)
        viz_section.add_option("Afficher noms", "labels", True)
        
        # Section Transformations
        transform_section = self.sidebar.add_section("Transformations")
        transform_section.add_option("Rotation (R/T)", "rotation_info", False)
        transform_section.add_option("Echelle (+/-)", "scale_info", False)
    
    def _setup_tool_buttons(self):
        """Configure les boutons d'outils"""
        start_x = 400
        y = 140
        spacing = 10
        
        self.tool_buttons.append(ToolButton("Effacer Tout", start_x, y, width=110))
        self.tool_buttons.append(ToolButton("Supprimer", start_x + 120, y, width=100))
        self.tool_buttons.append(ToolButton("Dupliquer", start_x + 230, y, width=100))
        self.tool_buttons.append(ToolButton("Annuler", start_x + 340, y, width=90))
        self.tool_buttons.append(ToolButton("Exporter", start_x + 440, y, width=90))
    
    def _on_option_change(self, option):
        """Callback quand une option change"""
        mode_options = ["draw_polygon", "draw_window", "select", "edit_vertices"]
        
        # Gestion des modes exclusifs
        if option.value in mode_options and option.enabled:
            for opt_name in mode_options:
                if opt_name != option.value:
                    opt = self.sidebar.get_option(opt_name)
                    if opt:
                        opt.enabled = False
            
            # Définir le mode
            if option.value == "draw_polygon":
                self.edit_mode = EditMode.DRAW_POLYGON
                self.status_text = "Mode: Dessin de polygone"
            elif option.value == "draw_window":
                self.edit_mode = EditMode.DRAW_WINDOW
                self.status_text = "Mode: Dessin de fenêtre"
            elif option.value == "select":
                self.edit_mode = EditMode.SELECT
                self.status_text = "Mode: Sélection"
            elif option.value == "edit_vertices":
                self.edit_mode = EditMode.EDIT_VERTICES
                self.status_text = "Mode: Édition de sommets"
        
        # Options d'algorithmes
        elif option.value == "clipping":
            self.show_clipping = option.enabled
            if self.realtime_mode and self.show_clipping:
                self._update_clipping()
        elif option.value == "filling":
            self.show_filling = option.enabled
            if self.realtime_mode and self.show_filling:
                self._update_filling()
        
        # Options de visualisation
        elif option.value == "grid":
            self.show_grid = option.enabled
        elif option.value == "vertices":
            self.show_vertices = option.enabled
        elif option.value == "labels":
            self.show_labels = option.enabled
        elif option.value == "realtime":
            self.realtime_mode = option.enabled
            if self.realtime_mode:
                self._update_clipping()
                self._update_filling()
    
    def _get_next_color(self) -> Tuple[int, int, int]:
        """Retourne la prochaine couleur pour un nouveau polygone"""
        color = self.polygon_colors[self.color_index]
        self.color_index = (self.color_index + 1) % len(self.polygon_colors)
        return color
    
    def _screen_to_world(self, screen_pos: Tuple[int, int]) -> Point:
        """Convertit les coordonnées écran en coordonnées monde"""
        x = (screen_pos[0] - self.pan_offset.x) / self.zoom
        y = (screen_pos[1] - self.pan_offset.y) / self.zoom
        return Point(x, y)
    
    def _world_to_screen(self, world_pos: Point) -> Tuple[int, int]:
        """Convertit les coordonnées monde en coordonnées écran"""
        x = int(world_pos.x * self.zoom + self.pan_offset.x)
        y = int(world_pos.y * self.zoom + self.pan_offset.y)
        return (x, y)
    
    def _update_clipping(self):
        """Met à jour le fenêtrage pour tous les polygones"""
        self.clipped_polygons.clear()
        
        if not self.show_clipping or self.polygon_manager.clipping_window is None:
            return
        
        clipper = SutherlandHodgman(self.polygon_manager.clipping_window)
        
        for poly in self.polygon_manager.polygons:
            if poly.is_visible and len(poly.vertices) >= 3:
                clipped = clipper.clip_polygon(poly)
                if len(clipped.vertices) >= 3:
                    clipped.color = poly.color
                    self.clipped_polygons.append(clipped)
    
    def _update_filling(self):
        """Met à jour le remplissage"""
        if self.fill_surface is None:
            self.fill_surface = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        self.fill_surface.fill((0, 0, 0, 0))
        
        if not self.show_filling:
            return
        
        lca = LCAFill()
        
        # Remplir les polygones clippés si le clipping est actif, sinon les originaux
        polygons_to_fill = self.clipped_polygons if self.show_clipping and self.clipped_polygons else self.polygon_manager.polygons
        
        for poly in polygons_to_fill:
            if poly.is_visible and len(poly.vertices) >= 3:
                segments = lca.fill_polygon(poly)
                fill_color = (*poly.color, 180)  # Avec transparence
                for p0, p1 in segments:
                    start = self._world_to_screen(p0)
                    end = self._world_to_screen(p1)
                    pygame.draw.line(self.fill_surface, fill_color, start, end, 1)
    
    def _finalize_polygon(self):
        """Finalise le polygone en cours de dessin"""
        if len(self.current_points) >= 3:
            if self.edit_mode == EditMode.DRAW_POLYGON:
                new_poly = Polygon(self.current_points.copy())
                new_poly.color = self._get_next_color()
                self.polygon_manager.add_polygon(new_poly)
                self.polygon_manager.select(len(self.polygon_manager) - 1)
                self.status_text = f"Polygone créé: {new_poly.name}"
            elif self.edit_mode == EditMode.DRAW_WINDOW:
                window = Polygon(self.current_points.copy(), "Fenêtre")
                window.color = (220, 20, 60)  # Rouge
                self.polygon_manager.set_clipping_window(window)
                self.status_text = "Fenêtre de clipping définie"
        
        self.current_points.clear()
        
        if self.realtime_mode:
            self._update_clipping()
            self._update_filling()
    
    def _delete_selected(self):
        """Supprime le polygone sélectionné ou le sommet sélectionné"""
        selected = self.polygon_manager.get_selected()
        if selected:
            if selected.selected_vertex_index is not None:
                # Supprimer le sommet sélectionné
                selected.remove_vertex(selected.selected_vertex_index)
                selected.selected_vertex_index = None
                self.status_text = "Sommet supprimé"
            else:
                # Supprimer le polygone entier
                idx = self.polygon_manager.selected_index
                self.polygon_manager.remove_polygon(idx)
                self.status_text = "Polygone supprimé"
            
            if self.realtime_mode:
                self._update_clipping()
                self._update_filling()
    
    def _duplicate_selected(self):
        """Duplique le polygone sélectionné"""
        selected = self.polygon_manager.get_selected()
        if selected:
            copy = selected.copy()
            copy.translate(20, 20)  # Décaler légèrement
            self.polygon_manager.add_polygon(copy)
            self.polygon_manager.select(len(self.polygon_manager) - 1)
            self.status_text = f"Polygone dupliqué: {copy.name}"
    
    def _export_polygons(self):
        """Exporte les polygones en JSON"""
        json_data = self.polygon_manager.to_json()
        
        # Sauvegarder dans un fichier
        filename = "polygons_export.json"
        try:
            with open(filename, 'w') as f:
                f.write(json_data)
            self.status_text = f"Exporté vers {filename}"
        except Exception as e:
            self.status_text = f"Erreur d'export: {e}"
    
    def handle_event(self, event: pygame.event.Event):
        """Gère les événements"""
        # Bouton retour
        if self.back_button.handle_event(event):
            self.app.navigate_to(PageType.HOME)
            return
        
        # Sidebar
        if self.sidebar.handle_event(event, self.screen.get_height()):
            return
        
        # Boutons outils
        for i, button in enumerate(self.tool_buttons):
            if button.handle_event(event):
                if i == 0:  # Effacer tout
                    self.polygon_manager.clear()
                    self.current_points.clear()
                    self.clipped_polygons.clear()
                    self.fill_surface = None
                    self.status_text = "Tout effacé"
                elif i == 1:  # Supprimer
                    self._delete_selected()
                elif i == 2:  # Dupliquer
                    self._duplicate_selected()
                elif i == 3:  # Annuler
                    if self.polygon_manager.undo():
                        self.status_text = "Annulé"
                        if self.realtime_mode:
                            self._update_clipping()
                            self._update_filling()
                elif i == 4:  # Exporter
                    self._export_polygons()
                return
        
        # Position de la souris
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self._handle_mouse_motion(event)
        
        # Clics souris
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_down(event)
        
        elif event.type == pygame.MOUSEBUTTONUP:
            self._handle_mouse_up(event)
        
        # Molette souris (zoom)
        elif event.type == pygame.MOUSEWHEEL:
            self._handle_mouse_wheel(event)
        
        # Clavier
        elif event.type == pygame.KEYDOWN:
            self._handle_key_down(event)
    
    def _handle_mouse_motion(self, event: pygame.event.Event):
        """Gère le mouvement de la souris"""
        if not self.canvas_rect.collidepoint(event.pos):
            return
        
        world_pos = self._screen_to_world(event.pos)
        
        # Pan
        if self.is_panning and self.pan_start:
            dx = event.pos[0] - self.pan_start.x
            dy = event.pos[1] - self.pan_start.y
            self.pan_offset = Point(
                self.pan_offset.x + dx,
                self.pan_offset.y + dy
            )
            self.pan_start = Point(event.pos[0], event.pos[1])
        
        # Drag d'un sommet
        elif self.dragged_vertex is not None:
            poly_idx, vertex_idx = self.dragged_vertex
            poly = self.polygon_manager.get_polygon(poly_idx)
            if poly:
                poly.move_vertex(vertex_idx, world_pos)
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # Drag d'un polygone
        elif self.dragged_polygon_idx is not None and self.drag_start:
            poly = self.polygon_manager.get_polygon(self.dragged_polygon_idx)
            if poly:
                dx = world_pos.x - self.drag_start.x
                dy = world_pos.y - self.drag_start.y
                poly.translate(dx, dy)
                self.drag_start = world_pos
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
    
    def _handle_mouse_down(self, event: pygame.event.Event):
        """Gère les clics souris"""
        if not self.canvas_rect.collidepoint(event.pos):
            return
        
        world_pos = self._screen_to_world(event.pos)
        
        # Clic gauche
        if event.button == 1:
            if self.edit_mode in [EditMode.DRAW_POLYGON, EditMode.DRAW_WINDOW]:
                # Ajouter un point
                self.current_points.append(world_pos)
                self.status_text = f"Point ajouté ({len(self.current_points)})"
            
            elif self.edit_mode == EditMode.SELECT:
                # Sélectionner un polygone
                idx = self.polygon_manager.select_at_point(world_pos)
                if idx is not None:
                    self.status_text = f"Sélectionné: {self.polygon_manager.get_polygon(idx).name}"
                    self.dragged_polygon_idx = idx
                    self.drag_start = world_pos
                else:
                    self.polygon_manager.select(None)
                    self.status_text = "Aucune sélection"
            
            elif self.edit_mode == EditMode.EDIT_VERTICES:
                # Trouver un sommet à éditer
                result = self.polygon_manager.find_vertex_at(world_pos, threshold=15/self.zoom)
                if result:
                    poly_idx, vertex_idx = result
                    self.polygon_manager.select(poly_idx)
                    poly = self.polygon_manager.get_polygon(poly_idx)
                    poly.selected_vertex_index = vertex_idx
                    self.dragged_vertex = result
                    self.status_text = f"Sommet {vertex_idx} sélectionné"
                else:
                    # Désélectionner
                    selected = self.polygon_manager.get_selected()
                    if selected:
                        selected.selected_vertex_index = None
        
        # Clic droit - fermer le polygone
        elif event.button == 3:
            if self.edit_mode in [EditMode.DRAW_POLYGON, EditMode.DRAW_WINDOW]:
                self._finalize_polygon()
        
        # Clic molette - pan
        elif event.button == 2:
            self.is_panning = True
            self.pan_start = Point(event.pos[0], event.pos[1])
    
    def _handle_mouse_up(self, event: pygame.event.Event):
        """Gère le relâchement de la souris"""
        if event.button == 1:
            self.dragged_vertex = None
            self.dragged_polygon_idx = None
            self.drag_start = None
        elif event.button == 2:
            self.is_panning = False
            self.pan_start = None
    
    def _handle_mouse_wheel(self, event: pygame.event.Event):
        """Gère la molette de la souris (zoom)"""
        if not self.canvas_rect.collidepoint(self.mouse_pos):
            return
        
        # Facteur de zoom
        zoom_factor = 1.1 if event.y > 0 else 0.9
        
        # Position de la souris avant zoom
        mouse_world_before = self._screen_to_world(self.mouse_pos)
        
        # Appliquer le zoom
        self.zoom *= zoom_factor
        self.zoom = max(0.1, min(5.0, self.zoom))  # Limites
        
        # Ajuster le pan pour zoomer vers la souris
        mouse_world_after = self._screen_to_world(self.mouse_pos)
        self.pan_offset = Point(
            self.pan_offset.x + (mouse_world_after.x - mouse_world_before.x) * self.zoom,
            self.pan_offset.y + (mouse_world_after.y - mouse_world_before.y) * self.zoom
        )
    
    def _handle_key_down(self, event: pygame.event.Event):
        """Gère les touches clavier"""
        # Échap - retour ou annuler dessin
        if event.key == pygame.K_ESCAPE:
            if self.current_points:
                self.current_points.clear()
                self.status_text = "Dessin annulé"
            else:
                self.app.navigate_to(PageType.HOME)
        
        # Suppr - supprimer sélection
        elif event.key == pygame.K_DELETE:
            self._delete_selected()
        
        # Ctrl+Z - Annuler
        elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.polygon_manager.undo():
                self.status_text = "Annulé"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # Ctrl+Y - Refaire
        elif event.key == pygame.K_y and pygame.key.get_mods() & pygame.KMOD_CTRL:
            if self.polygon_manager.redo():
                self.status_text = "Refait"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # Ctrl+D - Dupliquer
        elif event.key == pygame.K_d and pygame.key.get_mods() & pygame.KMOD_CTRL:
            self._duplicate_selected()
        
        # R - Rotation horaire
        elif event.key == pygame.K_r:
            selected = self.polygon_manager.get_selected()
            if selected:
                selected.rotate(math.radians(15))
                self.status_text = "Rotation +15°"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # T - Rotation anti-horaire
        elif event.key == pygame.K_t:
            selected = self.polygon_manager.get_selected()
            if selected:
                selected.rotate(math.radians(-15))
                self.status_text = "Rotation -15°"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # + - Agrandir
        elif event.key == pygame.K_PLUS or event.key == pygame.K_KP_PLUS:
            selected = self.polygon_manager.get_selected()
            if selected:
                selected.scale(1.1, 1.1)
                self.status_text = "Échelle +10%"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # - - Réduire
        elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
            selected = self.polygon_manager.get_selected()
            if selected:
                selected.scale(0.9, 0.9)
                self.status_text = "Échelle -10%"
                if self.realtime_mode:
                    self._update_clipping()
                    self._update_filling()
        
        # F - Remplir
        elif event.key == pygame.K_f:
            self.show_filling = not self.show_filling
            opt = self.sidebar.get_option("filling")
            if opt:
                opt.enabled = self.show_filling
            self._update_filling()
            self.status_text = f"Remplissage: {'ON' if self.show_filling else 'OFF'}"
        
        # G - Grille
        elif event.key == pygame.K_g:
            self.show_grid = not self.show_grid
            opt = self.sidebar.get_option("grid")
            if opt:
                opt.enabled = self.show_grid
        
        # Espace - Reset zoom/pan
        elif event.key == pygame.K_SPACE:
            self.zoom = 1.0
            self.pan_offset = Point(0, 0)
            self.status_text = "Vue réinitialisée"
    
    def update(self):
        """Mise à jour"""
        self.sidebar.update()
    
    def draw(self):
        """Dessine l'espace de travail"""
        work_area_x = self.sidebar.current_width
        
        # Zone de travail
        work_area_rect = pygame.Rect(
            work_area_x, 0,
            self.screen.get_width() - work_area_x,
            self.screen.get_height()
        )
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_CARD.rgb, work_area_rect)
        
        # Bouton retour
        self.back_button.rect.x = work_area_x + 30
        self.back_button.draw(self.screen)
        
        # Titre
        title = self.font_title.render("Espace de Travail Polygones", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        title_rect = title.get_rect(left=work_area_x + 200, top=35)
        self.screen.blit(title, title_rect)
        
        # Info polygones
        info_text = f"Polygones: {len(self.polygon_manager)} | Zoom: {self.zoom:.1f}x"
        info = self.font_small.render(info_text, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        self.screen.blit(info, (work_area_x + 200, 80))
        
        # Status
        if self.status_text:
            status = self.font_small.render(self.status_text, True, ColorPalette.MATHEMATICA_ORANGE.rgb)
            self.screen.blit(status, (work_area_x + 200, 105))
        
        # Boutons outils
        btn_x = work_area_x + 80
        for button in self.tool_buttons:
            button.rect.x = btn_x
            button.rect.y = 140
            button.draw(self.screen)
            btn_x += button.rect.width + 10
        
        # Canvas
        self.canvas_rect = pygame.Rect(
            work_area_x + 40, 200,
            self.screen.get_width() - work_area_x - 80,
            self.screen.get_height() - 240
        )
        pygame.draw.rect(self.screen, (255, 255, 255), self.canvas_rect, border_radius=8)
        
        # Clip au canvas
        self.screen.set_clip(self.canvas_rect)
        
        # Grille
        if self.show_grid:
            self._draw_grid()
        
        # Remplissage
        if self.fill_surface and self.show_filling:
            self.screen.blit(self.fill_surface, (0, 0))
        
        # Fenêtre de clipping
        if self.polygon_manager.clipping_window:
            self._draw_polygon(self.polygon_manager.clipping_window, is_window=True)
        
        # Polygones clippés ou originaux
        if self.show_clipping and self.clipped_polygons:
            for poly in self.clipped_polygons:
                self._draw_polygon(poly, is_clipped=True)
        else:
            for poly in self.polygon_manager.polygons:
                if poly.is_visible:
                    self._draw_polygon(poly)
        
        # Points en cours de dessin
        if self.current_points:
            self._draw_current_points()
        
        # Reset clip
        self.screen.set_clip(None)
        
        # Bordure du canvas
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_BORDER.rgb, self.canvas_rect, 2, border_radius=8)
        
        # Instructions si vide
        if len(self.polygon_manager) == 0 and not self.current_points:
            self._draw_instructions()
        
        # Liste des polygones (mini panel)
        self._draw_polygon_list()
        
        # Sidebar (dessiner en dernier)
        self.sidebar.draw(self.screen)
    
    def _draw_grid(self):
        """Dessine la grille"""
        grid_color = (230, 230, 230)
        grid_spacing = 50 * self.zoom
        
        # Lignes verticales
        start_x = self.canvas_rect.left + (self.pan_offset.x % grid_spacing)
        x = start_x
        while x < self.canvas_rect.right:
            pygame.draw.line(self.screen, grid_color, (int(x), self.canvas_rect.top), (int(x), self.canvas_rect.bottom))
            x += grid_spacing
        
        # Lignes horizontales
        start_y = self.canvas_rect.top + (self.pan_offset.y % grid_spacing)
        y = start_y
        while y < self.canvas_rect.bottom:
            pygame.draw.line(self.screen, grid_color, (self.canvas_rect.left, int(y)), (self.canvas_rect.right, int(y)))
            y += grid_spacing
    
    def _draw_polygon(self, poly: Polygon, is_window: bool = False, is_clipped: bool = False):
        """Dessine un polygone"""
        if len(poly.vertices) < 2:
            return
        
        # Convertir les sommets en coordonnées écran
        screen_points = [self._world_to_screen(p) for p in poly.vertices]
        
        # Couleur
        if is_window:
            color = (220, 20, 60)  # Rouge pour la fenêtre
            line_width = 3
        elif is_clipped:
            color = poly.color
            line_width = 2
        elif poly.is_selected:
            color = poly.color
            line_width = 3
        else:
            color = poly.color
            line_width = poly.line_width
        
        # Dessiner le polygone
        if len(screen_points) >= 3:
            # Contour
            pygame.draw.polygon(self.screen, color, screen_points, line_width)
            
            # Highlight si sélectionné
            if poly.is_selected and not is_window and not is_clipped:
                pygame.draw.polygon(self.screen, (*color, 50), screen_points, 0)
        else:
            # Juste une ligne
            pygame.draw.lines(self.screen, color, False, screen_points, line_width)
        
        # Sommets
        if self.show_vertices:
            for i, sp in enumerate(screen_points):
                # Couleur du sommet
                if poly.selected_vertex_index == i:
                    vertex_color = (255, 0, 0)  # Rouge pour le sommet sélectionné
                    radius = 8
                else:
                    vertex_color = (50, 50, 50)
                    radius = 5
                
                pygame.draw.circle(self.screen, vertex_color, sp, radius)
                pygame.draw.circle(self.screen, (255, 255, 255), sp, radius - 2)
        
        # Nom du polygone
        if self.show_labels and not is_clipped:
            center = poly.get_center()
            screen_center = self._world_to_screen(center)
            label = self.font_small.render(poly.name, True, (80, 80, 80))
            label_rect = label.get_rect(center=screen_center)
            
            # Fond du label
            bg_rect = label_rect.inflate(10, 4)
            pygame.draw.rect(self.screen, (255, 255, 255, 200), bg_rect, border_radius=3)
            self.screen.blit(label, label_rect)
    
    def _draw_current_points(self):
        """Dessine les points en cours de dessin"""
        if not self.current_points:
            return
        
        screen_points = [self._world_to_screen(p) for p in self.current_points]
        
        # Lignes
        if len(screen_points) > 1:
            pygame.draw.lines(self.screen, (100, 100, 100), False, screen_points, 2)
        
        # Ligne vers la souris
        if self.canvas_rect.collidepoint(self.mouse_pos):
            pygame.draw.line(self.screen, (150, 150, 150), screen_points[-1], self.mouse_pos, 1)
        
        # Points
        for sp in screen_points:
            pygame.draw.circle(self.screen, (50, 50, 50), sp, 6)
            pygame.draw.circle(self.screen, (255, 255, 255), sp, 4)
    
    def _draw_instructions(self):
        """Dessine les instructions quand le canvas est vide"""
        instructions = [
            "Clic gauche : ajouter un sommet",
            "Clic droit : fermer le polygone",
            "Molette : zoomer",
            "Clic molette : déplacer la vue",
            "R/T : rotation | +/- : échelle",
            "Suppr : supprimer | Ctrl+Z : annuler",
            "F : remplissage | G : grille",
            "Espace : réinitialiser la vue"
        ]
        
        y = self.canvas_rect.centery - len(instructions) * 15
        
        title_font = pygame.font.Font(None, 36)
        title = title_font.render("Zone de Dessin", True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        title_rect = title.get_rect(center=(self.canvas_rect.centerx, y - 40))
        self.screen.blit(title, title_rect)
        
        for instr in instructions:
            text = self.font_small.render(instr, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
            text_rect = text.get_rect(center=(self.canvas_rect.centerx, y))
            self.screen.blit(text, text_rect)
            y += 28
    
    def _draw_polygon_list(self):
        """Dessine la liste des polygones en bas à droite"""
        if len(self.polygon_manager) == 0:
            return
        
        panel_width = 200
        panel_height = min(30 + len(self.polygon_manager) * 25, 200)
        panel_x = self.screen.get_width() - panel_width - 20
        panel_y = self.screen.get_height() - panel_height - 20
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        
        # Fond
        pygame.draw.rect(self.screen, (255, 255, 255, 230), panel_rect, border_radius=8)
        pygame.draw.rect(self.screen, ColorPalette.MATHEMATICA_BORDER.rgb, panel_rect, 1, border_radius=8)
        
        # Titre
        title = self.font_small.render("Polygones", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        self.screen.blit(title, (panel_x + 10, panel_y + 5))
        
        # Liste
        y = panel_y + 30
        for i, poly in enumerate(self.polygon_manager.polygons):
            # Indicateur de couleur
            color_rect = pygame.Rect(panel_x + 10, y + 2, 12, 12)
            pygame.draw.rect(self.screen, poly.color, color_rect)
            
            # Nom
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb if poly.is_selected else ColorPalette.MATHEMATICA_SUBTEXT.rgb
            name = self.font_small.render(poly.name[:20], True, text_color)
            self.screen.blit(name, (panel_x + 28, y))
            
            # Highlight si sélectionné
            if poly.is_selected:
                highlight_rect = pygame.Rect(panel_x + 5, y - 2, panel_width - 10, 20)
                pygame.draw.rect(self.screen, (*ColorPalette.MATHEMATICA_ORANGE.rgb, 30), highlight_rect, border_radius=3)
            
            y += 25
            if y > panel_y + panel_height - 10:
                break