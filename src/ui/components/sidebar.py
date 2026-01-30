import pygame
from typing import List, Callable
from ..colors import ColorPalette


class ToggleOption:
    
    def __init__(self, label: str, value: any, enabled: bool = False):
        self.label = label
        self.value = value
        self.enabled = enabled
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.checkbox_rect = pygame.Rect(0, 0, 20, 20)
        self.is_hovered = False
        self.font = pygame.font.Font(None, 24)
    
    def draw(self, surface: pygame.Surface):
        bg_color = ColorPalette.MATHEMATICA_CARD.rgb if self.enabled else ColorPalette.MATHEMATICA_BG.rgb
        border_color = ColorPalette.MATHEMATICA_ORANGE.rgb if self.is_hovered else ColorPalette.MATHEMATICA_BORDER.rgb
        
        pygame.draw.rect(surface, bg_color, self.checkbox_rect, border_radius=4)
        pygame.draw.rect(surface, border_color, self.checkbox_rect, 2, border_radius=4)
        
        if self.enabled:
            check_points = [
                (self.checkbox_rect.left + 5, self.checkbox_rect.centery),
                (self.checkbox_rect.centerx - 2, self.checkbox_rect.bottom - 6),
                (self.checkbox_rect.right - 5, self.checkbox_rect.top + 5)
            ]
            pygame.draw.lines(surface, ColorPalette.MATHEMATICA_ORANGE.rgb, False, check_points, 3)
        
        text_color = ColorPalette.MATHEMATICA_TEXT.rgb if self.enabled else ColorPalette.MATHEMATICA_SUBTEXT.rgb
        text = self.font.render(self.label, True, text_color)
        text_rect = text.get_rect(left=self.checkbox_rect.right + 12, centery=self.checkbox_rect.centery)
        surface.blit(text, text_rect)


class SidebarSection:
    
    def __init__(self, title: str):
        self.title = title
        self.options: List[ToggleOption] = []
        self.font_title = pygame.font.Font(None, 28)
        self.rect = pygame.Rect(0, 0, 0, 0)
    
    def add_option(self, label: str, value: any, enabled: bool = False) -> ToggleOption:
        option = ToggleOption(label, value, enabled)
        self.options.append(option)
        return option
    
    def draw(self, surface: pygame.Surface, x: int, y: int, width: int) -> int:
        current_y = y
        
        title_text = self.font_title.render(self.title, True, ColorPalette.MATHEMATICA_TEXT.rgb)
        surface.blit(title_text, (x + 20, current_y))
        current_y += 40
        
        pygame.draw.line(
            surface,
            ColorPalette.MATHEMATICA_BORDER.rgb,
            (x + 20, current_y),
            (x + width - 20, current_y),
            1
        )
        current_y += 20
        
        for option in self.options:
            option.checkbox_rect = pygame.Rect(x + 20, current_y, 20, 20)
            option.rect = pygame.Rect(x + 20, current_y, width - 40, 30)
            option.draw(surface)
            current_y += 35
        
        return current_y - y + 15


class Sidebar:
    
    def __init__(self, width: int = 320, collapsed_width: int = 50):
        self.width = width
        self.collapsed_width = collapsed_width
        self.is_collapsed = False
        self.current_width = width
        
        self.animation_speed = 20
        self.target_width = width
        
        self.sections: List[SidebarSection] = []
        self.on_option_change: Callable = None
        
        self.toggle_button_rect = pygame.Rect(0, 0, 40, 40)
    
    def add_section(self, title: str) -> SidebarSection:
        section = SidebarSection(title)
        self.sections.append(section)
        return section
    
    def get_option(self, value: str) -> ToggleOption:
        for section in self.sections:
            for option in section.options:
                if option.value == value:
                    return option
        return None

    def toggle(self):
        self.is_collapsed = not self.is_collapsed
        self.target_width = self.collapsed_width if self.is_collapsed else self.width
    
    def handle_event(self, event: pygame.event.Event, screen_height: int):
        self.toggle_button_rect.topleft = (self.current_width - 40, 10)
        
        if event.type == pygame.MOUSEMOTION:
            if self.toggle_button_rect.collidepoint(event.pos):
                pass
            
            if not self.is_collapsed:
                for section in self.sections:
                    for option in section.options:
                        option.is_hovered = option.rect.collidepoint(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                if self.toggle_button_rect.collidepoint(event.pos):
                    self.toggle()
                    return True
                
                if not self.is_collapsed:
                    for section in self.sections:
                        for option in section.options:
                            if option.rect.collidepoint(event.pos):
                                option.enabled = not option.enabled
                                if self.on_option_change:
                                    self.on_option_change(option)
                                return True
        
        return False
    
    def update(self):
        if self.current_width != self.target_width:
            diff = self.target_width - self.current_width
            step = min(abs(diff), self.animation_speed)
            self.current_width += step if diff > 0 else -step
    
    def draw(self, surface: pygame.Surface):
        screen_height = surface.get_height()
        
        sidebar_rect = pygame.Rect(0, 0, self.current_width, screen_height)
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_CARD.rgb, sidebar_rect)
        
        pygame.draw.line(
            surface,
            ColorPalette.MATHEMATICA_BORDER.rgb,
            (self.current_width, 0),
            (self.current_width, screen_height),
            2
        )
        
        self.toggle_button_rect.topleft = (self.current_width - 45, 10)
        
        bg_color = ColorPalette.MATHEMATICA_ORANGE.rgb
        pygame.draw.rect(surface, bg_color, self.toggle_button_rect, border_radius=8)
        
        arrow_size = 10
        arrow_x = self.toggle_button_rect.centerx
        arrow_y = self.toggle_button_rect.centery
        
        if self.is_collapsed:
            arrow_points = [
                (arrow_x - 4, arrow_y - arrow_size),
                (arrow_x + 6, arrow_y),
                (arrow_x - 4, arrow_y + arrow_size)
            ]
        else:
            arrow_points = [
                (arrow_x + 4, arrow_y - arrow_size),
                (arrow_x - 6, arrow_y),
                (arrow_x + 4, arrow_y + arrow_size)
            ]
        
        pygame.draw.polygon(surface, ColorPalette.MATHEMATICA_CARD.rgb, arrow_points)
        
        if self.current_width > 100:
            current_y = 70
            for section in self.sections:
                height_used = section.draw(surface, 0, current_y, self.current_width)
                current_y += height_used
    
    def get_enabled_options(self) -> List[ToggleOption]:
        enabled = []
        for section in self.sections:
            for option in section.options:
                if option.enabled:
                    enabled.append(option)
        return enabled


class ToolButton:
    
    def __init__(self, label: str, x: int, y: int, width: int = 120, height: int = 40):
        self.label = label
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.is_active = False
        self.font = pygame.font.Font(None, 24)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False
    
    def draw(self, surface: pygame.Surface):
        if self.is_active:
            bg_color = ColorPalette.MATHEMATICA_ORANGE.rgb
            text_color = ColorPalette.MATHEMATICA_CARD.rgb
        elif self.is_hovered:
            bg_color = ColorPalette.MATHEMATICA_CARD_HOVER.rgb
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb
        else:
            bg_color = ColorPalette.MATHEMATICA_CARD.rgb
            text_color = ColorPalette.MATHEMATICA_TEXT.rgb
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_BORDER.rgb, self.rect, 2, border_radius=6)
        
        text = self.font.render(self.label, True, text_color)
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)