from Utils import Utils


class Pacman:
    """Classe propre à Pacman"""
    
    __slots__ = [
        "vies", "position", "vitesse", "etat", "orientation", "taillebloc",
        "future_orientation"
    ]

    def __init__(self, taillebloc):
        # INITIALISATION D'ATTRIBUTS
        self.taillebloc = taillebloc
        self.vies = 3
        self.position = (14 * taillebloc + 3 * taillebloc / 2,
                         29 * taillebloc + 3 * taillebloc / 2)
        self.vitesse = 3
        self.etat = False  # A mangé une pacgomme ?
        self.orientation = "N"  # Nord/Sud/Est/Ouest
        self.future_orientation = "N"

    def deplacement(self, carte):
        """
        Méthode qui s'occupe des déplacements de pacman sur la carte lui permettant d'avancer, de détecter les murs et de tourner. 

        Parameter:
        ----------
        carte(list): carte du jeu

        Returns
        -------
        None

        """
        x, y = self.position
        next_x, next_y = x, y
        # SI PACMAN EST AU MILIEU DE SA CASE ET QU'IL N'Y A PAS DE MUR VERS SA FUTURE ORIENTATION, IL TOURNE
        if self.future_orientation == "N" and not Utils.is_wall(
                x + (self.taillebloc / 2 - 1), y - (self.taillebloc - 1),
                self.taillebloc, carte) and not Utils.is_wall(
                    x - (self.taillebloc / 2 - 1), y -
                    (self.taillebloc - 1), self.taillebloc, carte):
            self.orientation = "N"
        elif self.future_orientation == "W" and not Utils.is_wall(
                x - (self.taillebloc - 1), y - (self.taillebloc / 2 - 1),
                self.taillebloc, carte) and not Utils.is_wall(
                    x - (self.taillebloc - 1), y +
                    (self.taillebloc / 2 - 1), self.taillebloc, carte):
            self.orientation = "W"
        elif self.future_orientation == "S" and not Utils.is_wall(
                x + (self.taillebloc / 2 - 1), y + (self.taillebloc - 1),
                self.taillebloc, carte) and not Utils.is_wall(
                    x - (self.taillebloc / 2 - 1), y +
                    (self.taillebloc - 1), self.taillebloc, carte):
            self.orientation = "S"
        elif self.future_orientation == "E" and not Utils.is_wall(
                x + (self.taillebloc - 1), y - (self.taillebloc / 2 - 1),
                self.taillebloc, carte) and not Utils.is_wall(
                    x + (self.taillebloc - 1), y +
                    (self.taillebloc / 2 - 1), self.taillebloc, carte):
            self.orientation = "E"

        # PACMAN AVANCE D'UN PIXEL DANS SA DIRECTION S'IL N'Y A PAS DE MUR DEVANT LUI
        if self.orientation == "N":
            next_y -= 1
            if not Utils.is_wall(next_x, next_y - self.taillebloc / 2,
                                 self.taillebloc, carte):
                self.position = (next_x, next_y)
        elif self.orientation == "S":
            next_y += 1
            if not Utils.is_wall(next_x, next_y + self.taillebloc / 2,
                                 self.taillebloc, carte):
                self.position = (next_x, next_y)
        elif self.orientation == "E":
            next_x += 1
            if not Utils.is_wall(next_x + self.taillebloc / 2, next_y,
                                 self.taillebloc, carte):
                self.position = (next_x, next_y)
        elif self.orientation == "W":
            next_x -= 1
            if not Utils.is_wall(next_x - self.taillebloc / 2, next_y,
                                 self.taillebloc, carte):
                self.position = (next_x, next_y)
