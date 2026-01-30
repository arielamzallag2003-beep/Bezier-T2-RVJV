import pygame
from typing import Dict
from .page_types import PageType
from .colors import ColorPalette
from .pages.home_page import HomePage
from .pages.polygon_workspace import PolygonWorkspace
from .pages.matrix_page import MatrixPage


class Application:
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.current_page_type = PageType.HOME
        self.pages: Dict[PageType, any] = {}
        
        self._init_pages()
        
        self.current_page = self.pages[PageType.HOME]
    
    def _init_pages(self):
        self.pages[PageType.HOME] = HomePage(self.screen, self)
        self.pages[PageType.POLYGON_WORKSPACE] = PolygonWorkspace(self.screen, self)
        self.pages[PageType.MATRIX] = MatrixPage(self.screen, self)
    
    def navigate_to(self, page_type: PageType):
        self.current_page_type = page_type
        self.current_page = self.pages[page_type]
        self.current_page.on_enter()
    
    def handle_event(self, event: pygame.event.Event):
        self.current_page.handle_event(event)
    
    def update(self):
        self.current_page.update()
    
    def draw(self):
        self.screen.fill(ColorPalette.MATHEMATICA_BG.rgb)
        self.current_page.draw()