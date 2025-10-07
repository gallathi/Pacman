from math import *


class Utils:
    """Classe des fonctions utiles pouvant servir à la fois aux fantômes, au modèle et à Pacman"""

    def is_wall(x, y, taillebloc, map):
        """
        Méthode permettant de vérifier si la case est un  mur.

        Parameters :
        ------
        x et y sont la position de la case à vérifier en pixels
        (Remarque : X et Y sont les coordonnées (non pixelisées) de la case à vérifier)
        
        Returns : 
        ------
        bool : True si la case est un mur, False sinon
        """

        X, Y = floor(x / taillebloc) - 1, floor(y / taillebloc) - 1
        if 0 <= Y < len(map) and 0 <= X < len(map[0]):
            return (map[Y][X] == "|" or map[Y][X] == "_")
