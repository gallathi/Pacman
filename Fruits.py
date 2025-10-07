import random
import pygame


class Fruits():
    """Classe propre aux fruits du jeu : fraises et pacgommes"""

    __slots__ = ['type', 'score', 'position', "map", "taillebloc"]

    def __init__(self, type, map, taillebloc):
        self.type = type
        self.score = 50
        self.position = (0, 0)
        self.map = map
        self.taillebloc = taillebloc
        self.positionnement()

    def fouiller_liste(self, Y):
        """
        Méthode qui renvoie la liste des index (coordonnées X)
        des termes de la forme '.' pour une ligne Y donnée

        Parameters
        ----------
        Y(int) : Coordonnées en Y (ligne de la grille)

        Returns
        -------
        liste(list) : Liste des index

        """
        liste = []
        index = 1
        while index < len(self.map[0]) - 1:
            if self.map[Y][index] == '.':
                liste.append(index)
            index += 1
        return (liste)

    def positionnement(self):
        """
        Méthode qui positionne aléatoirement les fruits et pacgommes sur la map
        Ceux-ci doivent être positionnés sur un '.' dans le
        cas contraire, elle le positionne sur le '.' le plus proche.

        Returns
        -------
        None.

        """
        self.position = (14, 29)
        while self.position == (14, 29):
            # CHOISIT UNE LIGNE ALEATOIRE
            Y_coord = random.randint(1, len(self.map) - 2)
            while self.fouiller_liste(Y_coord) == []:
                Y_coord = random.randint(0, len(self.map) - 1)
            # CHOISIT UNE COLONNE PARMI CELLES LIBRES DANS LA LIGNE Y
            X_possibles = self.fouiller_liste(Y_coord)
            X_coord = random.choice(X_possibles)
            self.position = (X_coord, Y_coord)

        # TRANSFORME LES COORDONNES DE LISTE EN COORDONNES EN PIXELS
        x_coord = X_coord * self.taillebloc + 1.5 * self.taillebloc
        y_coord = Y_coord * self.taillebloc + 1.5 * self.taillebloc
        self.position = (x_coord, y_coord)

    def disparition(self):
        """
        Méthode qui initialise le timer de respawn des fruits et de durée de la pacgomme quand un des         2 est mangé.

        Returns
        -------
        - fruit (int) : compteur de respawn du fruit
        - pacgomme (int) : compteur de durée de la pacgomme

        """
        fruit, pacgomme = 0, 0

        # SON DE PACMAN MANGEANT LE FRUIT
        son = pygame.mixer.Sound("son/fruit.ogg")
        son.play()
        son.set_volume(0.4)

        if self.type == 'pacgomme':
            pacgomme = 8
        elif self.type == "fruit":
            fruit = 4
        return fruit, pacgomme
