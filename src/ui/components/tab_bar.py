import pygame
from typing import List, Callable
from ..colors import ColorPalette


class Tab:

    def __init__(self, label: str, value: any):
        self.label = label
        self.value = value
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.Font(None, 28)
    
    def draw(self, surface: pygame.Surface):
        if self.is_active:
            bg_color = ColorPalette.MATHEMATICA_CARD.rgb
            text_color = ColorPalette.MATHEMATICA_ORANGE.rgb
            border_bottom = True
        elif self.is_hovered:
            bg_color = ColorPalette.MATHEMATICA_CARD_HOVER.rgb
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb
            border_bottom = False
        else:
            bg_color = ColorPalette.MATHEMATICA_BG.rgb
            text_color = ColorPalette.MATHEMATICA_SUBTEXT.rgb
            border_bottom = False
        
        pygame.draw.rect(surface, bg_color, self.rect)
        
        if border_bottom:
            pygame.draw.line(
                surface,
                ColorPalette.MATHEMATICA_ORANGE.rgb,
                (self.rect.left, self.rect.bottom - 2),
                (self.rect.right, self.rect.bottom - 2),
                3
            )
        
        text = self.font.render(self.label, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)


class TabBar:

    def __init__(self, x: int, y: int, width: int, height: int = 50):
        self.rect = pygame.Rect(x, y, width, height)
        self.tabs: List[Tab] = []
        self.active_tab_index = 0
        self.on_change: Callable = None
    
    def add_tab(self, label: str, value: any):
        tab = Tab(label, value)
        self.tabs.append(tab)
        self._update_tab_positions()
    
    def _update_tab_positions(self):
        if not self.tabs:
            return
        
        tab_width = self.rect.width // len(self.tabs)
        
        for i, tab in enumerate(self.tabs):
            tab.rect = pygame.Rect(
                self.rect.x + i * tab_width,
                self.rect.y,
                tab_width,
                self.rect.height
            )
            tab.is_active = (i == self.active_tab_index)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            for tab in self.tabs:
                tab.is_hovered = tab.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for i, tab in enumerate(self.tabs):
                    if tab.rect.collidepoint(event.pos):
                        if i != self.active_tab_index:
                            self.active_tab_index = i
                            self._update_tab_positions()
                            if self.on_change:
                                self.on_change(tab.value)
                            return True
        
        return False
    
    def get_active_value(self):
        if self.tabs:
            return self.tabs[self.active_tab_index].value
        return None
    
    def draw(self, surface: pygame.Surface):
        pygame.draw.line(
            surface,
            ColorPalette.MATHEMATICA_BORDER.rgb,
            (self.rect.left, self.rect.bottom),
            (self.rect.right, self.rect.bottom),
            1
        )
        
        # Onglets
        for tab in self.tabs:
            tab.draw(surface)