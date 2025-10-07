from Utils import Utils
import random
from Pacman import Pacman
from collections import deque
import random
from math import *
import heapq   # utilisation des files de priorité 


########################### Stratégies des fantômes #######################################
# - Blinky (rouge) : c'est le plus agressif et le plus rapide. Il suit Pacman de très près.
# - Pinky (rose) : c'est le plus malin, il essaie de s'interposer devant Pacman.
# - Inky (bleu) : c'est le plus réservé, il suit souvent Blinky.
# - Clyde (jaune) : c'est le plus lent et le moins agressif, il a tendance à errer.


class Fantome():
    """Classe propre aux 4 fantômes : Inky, Blinky, Pinky et Clyde """
    
    __slots__ = [
        "nom", "apparence", "position", "vitesse", "taillebloc", "etat",
        "cible", "fuite", "mort"
    ]

    def __init__(self, nom, apparence, position, taillebloc, map):
        self.nom = nom
        self.taillebloc = taillebloc
        self.apparence = apparence
        self.position = position
        self.vitesse = 2
        self.etat = False  # subit une pacgomme ou pas
        self.fuite = []
        self.mort = False
        if self.nom == "clyde":  # Clyde se dirige toujours vers une cible aléatoire
            self.cible = self.chercher_cible(map)

    def chercher_cible(self, map):
        """
        Méthode qui permet à Clyde de déterminer sa prochaine position qui est aléatoire sur la map

        Parameters
        ----------
        map (list 2D) : map du jeu

        Returns
        -------
        Ycible (int) : prochaine coordonnée en Y de Clyde
        Xcible (int) : prochaine coordonnée en X de Clyde

        """
        Ycible = random.randint(2, 28)
        Xcible = random.choice(self.fouiller_liste(Ycible, map))
        return (Ycible, Xcible)

    def deplacement(self, pacman_position, taillebloc, map, pacman_orientation,
                    blinky_position):
        """ 
        Méthode qui permet de piloter le déplacement des 4 fantômes sur la map selon la stratégie de chacun.
        
        Parameters
        ----------
        pacman_position (tuple) : position de pacman
        taillebloc (int) : taille d'un bloc
        map (list 2D) : map du jeu
        pacman_orientation (str) : orientation de pacman
        blinky_position (tuple) : position de blinky
        
        Returns
        -------
        Ycible (int): prochaine coordonnée en Y de Clyde
        Xcible (int): prochaine coordonnée en X de Clyde

        """
        xpac, ypac = pacman_position
        Xpac, Ypac = floor(xpac / taillebloc) - 1, floor(ypac / taillebloc) - 1
        x, y = self.position[0], self.position[1]
        X, Y = floor(x / taillebloc) - 1, floor(y / taillebloc) - 1

        # MOUVEMENT BLINKY : ESSAIE D'ALLER SUR PACMAN
        if self.nom == "blinky":
            mouvement = self.find_plus_court_chemin(map, (Y, X), (Ypac, Xpac),
                                                    (11, 12), self.etat,
                                                    (Xpac, Ypac))

        # MOUVEMENT INKY : SUIT BLINKY ET RETOURNE A SA POSITION DE DEPART S'IL EST TROP PRES DE LUI
        elif self.nom == "inky":
            xb, yb = blinky_position
            Xb, Yb = floor(xb / taillebloc) - 1, floor(yb / taillebloc) - 1
            if sqrt((X - Xb)**2) < 6 and sqrt((Y - Yb)**2) < 6:
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X), (11, 13), (11, 13), self.etat, (Xpac, Ypac))
            else:
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X), (Yb, Xb), (11, 13), self.etat, (Xpac, Ypac))

        # MOUVEMENT PINKY : ESSAIE D'ALLER 3 CASES DEVANT PACMAN, SINON 2, SINON 1, SINON SUR PACMAN
        elif self.nom == "pinky":
            direction = self.recuperer_orientation(pacman_orientation)
            if 3 <= Xpac <= 24 and 3 <= Ypac <= 27 and not Utils.is_wall(
                    xpac + 3 * taillebloc * direction[0],
                    ypac + 3 * taillebloc * direction[1], taillebloc, map):
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X),
                    (Ypac + 3 * direction[1], Xpac + 3 * direction[0]),
                    (11, 14), self.etat, (Xpac, Ypac))
            elif 2 <= Xpac <= 25 and 2 <= Ypac <= 26 and not Utils.is_wall(
                    xpac + 2 * taillebloc * direction[0],
                    ypac + 2 * taillebloc * direction[1], taillebloc, map):
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X),
                    (Ypac + 2 * direction[1], Xpac + 2 * direction[0]),
                    (11, 14), self.etat, (Xpac, Ypac))
            elif 1 <= Xpac <= 26 and 1 <= Ypac <= 27 and not Utils.is_wall(
                    xpac + taillebloc * direction[0],
                    ypac + taillebloc * direction[1], taillebloc, map):
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X), (Ypac + direction[1], Xpac + direction[0]),
                    (11, 14), self.etat, (Xpac, Ypac))
            else:
                mouvement = self.find_plus_court_chemin(
                    map, (Y, X), (Ypac, Xpac), (11, 14), self.etat,
                    (Xpac, Ypac))

        # MOUVEMENT CLYDE : VA A UNE POSITION ALEATOIRE QUI CHANGE DES QU'IL L'ATTEINT
        elif self.nom == "clyde":
            if (Y, X) == self.cible:
                self.cible = self.chercher_cible(map)
            mouvement = self.find_plus_court_chemin(map, (Y, X), self.cible,
                                                    (11, 15), self.etat,
                                                    (Xpac, Ypac))
        else:
            mouvement = [0, 0]

        # VERIFICATION QUE LE FANTOME EST BIEN AU MILIEU DE SA CASE SI IL VEUT TOURNER
        if mouvement[0] == 0 and x % taillebloc not in [
                taillebloc / 2 - 1, taillebloc / 2
        ]:
            if x % taillebloc > taillebloc / 2:
                mouvement = [-1, 0]
            else:
                mouvement = [1, 0]
        elif mouvement[1] == 0 and y % taillebloc not in [
                taillebloc / 2 - 1, taillebloc / 2
        ]:
            if y % taillebloc > taillebloc / 2:
                mouvement = [0, -1]
            else:
                mouvement = [0, 1]

        # APPLICATION DE LA POSITION
        self.position = (x + mouvement[0], y + mouvement[1])

    def find_plus_court_chemin(self, map, pos_f, pos_cible, pos_init_f, etat,
                               pacman_position):
        """Méthode qui lance la détermination du plus court chemin entre les fantômes et leur destination cible ou vers leur position initiale lorsqu'ils sont vulnérables à cause d'une pacgomme
        
    Parameters :
    -------
    - pos_f (tuple) : position (X, Y) actuelle du fantôme à l'instant
    - pos_cible (tuple) : position (X, Y) ciblée par le fantôme
    - pos_init_f (tuple): position (X, Y) initiale du fantôme en question
    - etat (bool) : état de vulnérabilité du fantôme
    
    Returns : 
    -------
    - direction : liste [x, y] indiquant dans quelle direction devrait aller le fantôme (ex : [0, -1] pour aller vers le haut(y décroissants))
        """

        # SI FANTOME SOUS EFFET DE PACGOMME, IL RETOURNE A SA POSITION DE DEPART
        if self.etat:
            Xpac, Ypac = pacman_position
            Y, X = pos_f
            # SI FANTOME SOUS EFFET DE PACGOMME ET PACMAN TRES PROCHE DE LUI, IL FUIT DANS UNE DIRECTION ALEATOIRE
            if sqrt((Xpac - X)**2) < 4 and sqrt((Ypac - Y)**2) < 4:
                if self.fuite == []:
                    self.fuite = self.chercher_cible(map)
                direction = self.bfs(map, pos_f, self.fuite)
            else:
                direction = self.bfs(map, pos_f, pos_init_f)

        # SINON, IL VA A SA POSITION CIBLE
        else:
            self.fuite = []
            direction = self.bfs(map, pos_f, pos_cible)
        return direction

    def replacement(self):
        """
        Méthode qui convertit la position de chaque fantôme initialement en pixels en une position de type "case" 

        Returns
        -------
        None.
        
        """
        if self.nom == "blinky":
            self.position = (12 * self.taillebloc + 3 * self.taillebloc / 2,
                             11 * self.taillebloc + 3 * self.taillebloc / 2)
        elif self.nom == "inky":
            self.position = (13 * self.taillebloc + 3 * self.taillebloc / 2,
                             11 * self.taillebloc + 3 * self.taillebloc / 2)
        elif self.nom == "pinky":
            self.position = (14 * self.taillebloc + 3 * self.taillebloc / 2,
                             11 * self.taillebloc + 3 * self.taillebloc / 2)
        elif self.nom == "clyde":
            self.position = (15 * self.taillebloc + 3 * self.taillebloc / 2,
                             11 * self.taillebloc + 3 * self.taillebloc / 2)

    def reconstruct_path(self, came_from, current):  ## FONCTION MAJORIRAIREMENT INSPIREE DE CHATGPT ##
        """
            Méthode qui reconstruit le chemin en suivant les noeuds parents de la cible au point de              départ
            
            Parameters :
            -------
            came_from (dict): permet de garder une trace des nœuds parents 
            current (tuple):

            Returns : 
            -------
            total_path (list de tuple): l'ensemble des cases constituant le chemin du personnage

        """
        total_path = [current]
        while current in came_from:
            current = came_from[current] #pour chaque case, on récupère la case parent dans le chemin le plus court 
            total_path.append(current)
        total_path.reverse() #on inverse cette liste pour être dans le bon ordre (depuis la case de départ à la case d'arrivée)
        return total_path

    def dijkstra(self, map, pos_init, pos_fin):  ## FONCTION MAJORIRAIREMENT INSPIREE DE CHATGPT ##
        """
            Méthode qui permet de calculer le plus court chemin entre deux points sur une map. 
           
            Parameters :
            -------
            map (list 2D) : map du jeu
            pos_init (tuple) : position initiale
            pos_fin (tuple) : position cible

            Returns : 
            -------
            - total_path (list de tuple): l'ensemble des cases constituant le chemin du personnage
            - liste vide si aucun chemin n'est possible


        """
        rows, cols = len(map), len(map[0])
        open_set = [(0, pos_init)]  # file de priorité qu'on initialise avec le coût initial depuis la première case, et la position de celle-ci
        came_from = {} #dictionnaire qui garde en mémoire les nœuds parents
        g_score = {pos_init: 0} #dictionnaire qui garde pour chaque case, la meilleure distance connue entre lui et le point de départ

        while open_set:
            current_g, current = heapq.heappop(open_set) #récupère et retire le noeud avec le coût/ distance la plus faible

            if current == pos_fin:
                return self.reconstruct_path(came_from, current)

            for direction in [(1,0), (0,1), (-1,0), (0,-1)]: #pour chaque direction, on calcule les coordonnées du voisin
                neighbor = (current[0] + direction[0],
                            current[1] + direction[1])
                if 0 <= neighbor[0] < rows and 0 <= neighbor[1] < cols and map[neighbor[0]][neighbor[1]] == '.': 
                    tentative_g_score = current_g + 1 #on calcule le cout/score temporaire pour atteindre cette case

                    if neighbor not in g_score or tentative_g_score < g_score[neighbor]: #Si cette case n'a pas encore été explorée ou si le nouveau score est meilleur que le score précédent, les dictionnaires came_from et g_score sont mis à jour.
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g_score
                        heapq.heappush(open_set, (tentative_g_score, neighbor)) #le voisin est ajouté à open_set avec son score
        return []

    def bfs(self, map, pos_init, pos_fin):
        """
        Algorithme qui cherche le chemin le plus court entre deux points sur une map et qui renvoie le déplacement à effectuer

        Parameters
        --------
        map (list 2D) : map du jeu
        pos_init (tuple) : position initiale
        pos_fin (tuple) : position cible

        Returns
        -------
        deplacement (list): déplacement que doit effectuer le fantôme depuis sa position vers la prochaine position qui correspond au premier noeud du plus court chemin renvoyé par la fonction djikstra
        """
        
        chemin = self.dijkstra(map, pos_init, pos_fin) #on trouve le chemin le plus cour à l'aide de l'algo de dijkstra
        x1, y1 = chemin[0] #on récupère les coordonées de la première case de ce chemin (et donc la case suivante dans notre jeu)
        if (len(chemin) == 1) or (len(chemin)) == 0: 
            x2, y2 = x1, y1
        else:
            x2, y2 = chemin[1]
        deplacement = [y2 - y1, x2 - x1]
        return deplacement

    def fouiller_liste(self, Y, map):
        """
        Méthode qui renvoie la liste des index (coordonnées Y) des termes de la forme '.' dans une           ligne X donnée

        Parameters
        ----------
        Y (int) : Coordonnées en Y (ligne de la grille)

        Returns
        -------
        liste (list) : Liste des index

        """
        
        liste = []
        index = 1
        while index < len(map[0]) - 1:
            if map[Y][index] == '.':
                liste.append(index)
            index += 1
        return (liste)

    def recuperer_orientation(self, orientation):
        """
        Méthode qui renvoie l'orientation de Pacman sous le format X, Y

        Parameters
        ----------
        orientation (str) : orientation N/S/E/W de Pacman

        Returns
        -------
        liste de la direction (X, Y) correspondant à l'orientation de Pacman

        """
        if orientation == "N":
            return [0, -1]
        elif orientation == "S":
            return [0, 1]
        elif orientation == "W":
            return [-1, 0]
        else:
            return [1, 0]