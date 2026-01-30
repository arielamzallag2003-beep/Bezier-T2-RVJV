"""
Page d'accueil - Menu principal de l'application
"""

import pygame
from .base_page import BasePage
from ..colors import ColorPalette
from ..page_types import PageType


class MenuCard:
    """Carte de menu cliquable"""
    
    def __init__(self, title: str, subtitle: str, description: str, 
                 page_type: PageType, x: int, y: int, 
                 width: int, height: int, enabled: bool = True):
        self.title = title
        self.subtitle = subtitle
        self.description = description
        self.page_type = page_type
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.enabled = enabled
        self.font_title = pygame.font.Font(None, 38)
        self.font_subtitle = pygame.font.Font(None, 24)
        self.font_desc = pygame.font.Font(None, 20)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Gère les événements"""
        if not self.enabled:
            return False
            
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False
    
    def draw(self, surface: pygame.Surface):
        """Dessine la carte"""
        if not self.enabled:
            bg_color = (240, 240, 240)
            border_color = ColorPalette.MATHEMATICA_BORDER.rgb
            text_color = ColorPalette.TEXT_DISABLED.rgb
            border_width = 1
        elif self.is_hovered:
            bg_color = ColorPalette.MATHEMATICA_CARD_HOVER.rgb
            border_color = ColorPalette.MATHEMATICA_ORANGE.rgb
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb
            border_width = 3
        else:
            bg_color = ColorPalette.MATHEMATICA_CARD.rgb
            border_color = ColorPalette.MATHEMATICA_BORDER.rgb
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb
            border_width = 2
        
        # Fond
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=12)
        
        # Bordure
        pygame.draw.rect(surface, border_color, self.rect, border_width, border_radius=12)
        
        # Titre
        title_surface = self.font_title.render(self.title, True, text_color)
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, top=self.rect.top + 30)
        surface.blit(title_surface, title_rect)
        
        # Ligne décorative
        line_y = title_rect.bottom + 15
        pygame.draw.line(
            surface,
            ColorPalette.MATHEMATICA_BORDER.rgb,
            (self.rect.left + 30, line_y),
            (self.rect.right - 30, line_y),
            1
        )
        
        # Sous-titre
        subtitle_color = ColorPalette.MATHEMATICA_ORANGE.rgb if self.enabled else ColorPalette.TEXT_DISABLED.rgb
        subtitle_surface = self.font_subtitle.render(self.subtitle, True, subtitle_color)
        subtitle_rect = subtitle_surface.get_rect(centerx=self.rect.centerx, top=line_y + 15)
        surface.blit(subtitle_surface, subtitle_rect)
        
        # Description
        desc_color = ColorPalette.MATHEMATICA_SUBTEXT.rgb if self.enabled else ColorPalette.TEXT_DISABLED.rgb
        desc_surface = self.font_desc.render(self.description, True, desc_color)
        desc_rect = desc_surface.get_rect(centerx=self.rect.centerx, top=subtitle_rect.bottom + 10)
        surface.blit(desc_surface, desc_rect)
        
        # Badge "Nouveau" ou "W.I.P"
        if not self.enabled:
            badge_text = "W.I.P"
            badge_color = ColorPalette.MATHEMATICA_SUBTEXT.rgb
        elif self.page_type == PageType.BEZIER_WORKSPACE:
            badge_text = "T2"
            badge_color = ColorPalette.SUCCESS.rgb
        else:
            badge_text = None
            badge_color = None
        
        if badge_text:
            badge_font = pygame.font.Font(None, 18)
            badge_surface = badge_font.render(badge_text, True, (255, 255, 255))
            badge_rect = badge_surface.get_rect()
            badge_bg = pygame.Rect(
                self.rect.right - badge_rect.width - 25,
                self.rect.top + 10,
                badge_rect.width + 10,
                badge_rect.height + 6
            )
            pygame.draw.rect(surface, badge_color, badge_bg, border_radius=4)
            badge_rect.center = badge_bg.center
            surface.blit(badge_surface, badge_rect)


class HomePage(BasePage):
    """Page d'accueil avec le menu principal"""
    
    def __init__(self, screen: pygame.Surface, app):
        super().__init__(screen, app)
        self.cards = []
        self._setup_cards()
    
    def _setup_cards(self):
        """Configure les cartes du menu"""
        card_width = 350
        card_height = 180
        spacing = 40
        
        # Calculer la position pour centrer 3 cartes
        total_width = 3 * card_width + 2 * spacing
        start_x = (self.screen.get_width() - total_width) // 2
        start_y = 280
        
        # Carte 1: Polygones (T1)
        self.cards.append(MenuCard(
            title="Polygones",
            subtitle="Fenêtrage & Remplissage",
            description="Sutherland-Hodgman, LCA Fill",
            page_type=PageType.POLYGON_WORKSPACE,
            x=start_x, y=start_y,
            width=card_width, height=card_height,
            enabled=True
        ))
        
        # Carte 2: Courbes de Bézier (T2)
        self.cards.append(MenuCard(
            title="Courbes de Bézier",
            subtitle="Génération & Raccordements",
            description="Casteljau, Pascal, C0/C1/C2",
            page_type=PageType.BEZIER_WORKSPACE,
            x=start_x + card_width + spacing, y=start_y,
            width=card_width, height=card_height,
            enabled=False  # À activer quand implémenté
        ))
        
        # Carte 3: Matrices
        self.cards.append(MenuCard(
            title="Matrices",
            subtitle="Transformations Géométriques",
            description="Translation, Rotation, Échelle",
            page_type=PageType.MATRIX,
            x=start_x + 2 * (card_width + spacing), y=start_y,
            width=card_width, height=card_height,
            enabled=True
        ))
    
    def handle_event(self, event: pygame.event.Event):
        """Gère les événements"""
        for card in self.cards:
            if card.handle_event(event):
                self.app.navigate_to(card.page_type)
    
    def update(self):
        """Mise à jour"""
        pass
    
    def draw(self):
        """Dessine la page d'accueil"""
        # Titre principal
        title = self.font_title.render("Mathématiques pour l'Infographie", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 70))
        self.screen.blit(title, title_rect)
        
        # Sous-titre
        subtitle = self.font_normal.render("EFREI Paris - M1 VR & Jeux Vidéo - 2025/2026", True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        subtitle_rect = subtitle.get_rect(center=(self.screen.get_width() // 2, 120))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Ligne décorative
        pygame.draw.line(
            self.screen,
            ColorPalette.MATHEMATICA_BORDER.rgb,
            (250, 160),
            (self.screen.get_width() - 250, 160),
            2
        )
        
        # Description des projets
        desc_y = 200
        desc_font = pygame.font.Font(None, 22)
        
        descriptions = [
            "T1: Fenêtrage (Sutherland-Hodgman) et Remplissage (LCA)",
            "T2: Courbes de Bézier, Casteljau, Raccordements C0/C1/C2"
        ]
        
        for desc in descriptions:
            desc_text = desc_font.render(desc, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
            desc_rect = desc_text.get_rect(center=(self.screen.get_width() // 2, desc_y))
            self.screen.blit(desc_text, desc_rect)
            desc_y += 28
        
        # Dessiner les cartes
        for card in self.cards:
            card.draw(self.screen)
        
        # Instructions en bas
        footer_y = self.screen.get_height() - 80
        
        instructions = [
            "Sélectionnez un module pour commencer",
            "Utilisez ESC pour revenir au menu depuis n'importe quelle page"
        ]
        
        for instr in instructions:
            footer_text = self.font_small.render(instr, True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
            footer_rect = footer_text.get_rect(center=(self.screen.get_width() // 2, footer_y))
            self.screen.blit(footer_text, footer_rect)
            footer_y += 25
        
        # Version
        version_text = self.font_small.render("v1.1 - Projet T1/T2", True, ColorPalette.MATHEMATICA_SUBTEXT.rgb)
        version_rect = version_text.get_rect(bottomright=(self.screen.get_width() - 20, self.screen.get_height() - 10))
        self.screen.blit(version_text, version_rect)