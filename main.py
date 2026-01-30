"""
Projet: Fenêtrage et Remplissage de Polygones
Auteur: Ariel, Enzo, Théo
Date: 2026

Point d'entrée principal de l'application
"""

import pygame
from src.ui.application import Application
from src.ui.window import WindowConfig


def main():
    """Point d'entrée principal de l'application"""
    # Initialisation de Pygame
    pygame.init()
    
    # Configuration de la fenêtre
    config = WindowConfig()
    screen = pygame.display.set_mode((config.width, config.height))
    pygame.display.set_caption(config.title)
    
    # Création de l'application
    app = Application(screen)
    
    # Boucle principale
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Gestion des événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                app.handle_event(event)
        
        # Mise à jour
        app.update()
        
        # Rendu
        app.draw()
        pygame.display.flip()
        
        # Limitation FPS
        clock.tick(60)
    
    pygame.quit()


if __name__ == "__main__":
    main()