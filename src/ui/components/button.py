import pygame
from ..colors import ColorPalette


class BackButton:
    
    def __init__(self, x: int, y: int, width: int = 120, height: int = 50):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_hovered = False
        self.font = pygame.font.Font(None, 26)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            return False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                return True
        return False
    
    def draw(self, surface: pygame.Surface):
        bg_color = ColorPalette.MATHEMATICA_ORANGE.rgb if self.is_hovered else ColorPalette.MATHEMATICA_CARD.rgb
        
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=8)
        
        pygame.draw.rect(surface, ColorPalette.MATHEMATICA_BORDER.rgb, self.rect, 2, border_radius=8)
        
        arrow_size = 8
        arrow_x = self.rect.left + 25
        arrow_y = self.rect.centery
        
        arrow_points = [
            (arrow_x, arrow_y),                       
            (arrow_x + arrow_size, arrow_y - arrow_size), 
            (arrow_x + arrow_size, arrow_y + arrow_size) 
        ]
        
        pygame.draw.polygon(surface, ColorPalette.MATHEMATICA_TEXT.rgb, arrow_points)
        
        pygame.draw.line(
            surface,
            ColorPalette.MATHEMATICA_TEXT.rgb,
            (arrow_x + arrow_size, arrow_y),
            (arrow_x + arrow_size + 12, arrow_y),
            2
        )
        
        text = self.font.render("Retour", True, ColorPalette.MATHEMATICA_TEXT.rgb)
        text_rect = text.get_rect(left=arrow_x + arrow_size + 20, centery=arrow_y)
        surface.blit(text, text_rect)