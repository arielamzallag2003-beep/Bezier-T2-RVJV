import pygame
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..application import Application


class BasePage(ABC):
    
    def __init__(self, screen: pygame.Surface, app: 'Application'):
        self.screen = screen
        self.app = app
        self.font_title = pygame.font.Font(None, 48)
        self.font_normal = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)
    
    def on_enter(self):
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass
    
    @abstractmethod
    def update(self):
        pass
    
    @abstractmethod
    def draw(self):
        pass