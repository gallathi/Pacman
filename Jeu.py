import random
from Pacman import Pacman
from Fantome import Fantome
from Fruits import Fruits
import random


class Jeu():
  """
   Classe faisant office de modèle du jeu, elle gère l’initialisation, la création des éléments de jeu et leurs déplacements/modifications
  """
  
  __slots__ = [
      "map", "personnages", "score", "taillebloc", "points_restants", "fruits",
      "taillebloc"
  ]

  def __init__(self, taillebloc):
    self.taillebloc = taillebloc
    self.score = 0 # Initialise le score
    self.creation_map("Maps.txt") # Crée une carte de jeu
    
    # INITIE LES PERSONNAGES A LEURS POSITIONS INITIALES
    self.personnages = [
        Pacman(taillebloc),
        Fantome("blinky", "image/blinky.png",
                (12 * taillebloc + 3 * taillebloc / 2,
                 11 * taillebloc + 3 * taillebloc / 2), taillebloc, self.map),
        Fantome("inky", "image/inky.png",
                (13 * taillebloc + 3 * taillebloc / 2,
                 11 * taillebloc + 3 * taillebloc / 2), taillebloc, self.map),
        Fantome("pinky", "image/pinky.png",
                (14 * taillebloc + 3 * taillebloc / 2,
                 11 * taillebloc + 3 * taillebloc / 2), taillebloc, self.map),
        Fantome("clyde", "imageclyde.png",
                (15 * taillebloc + 3 * taillebloc / 2,
                 11 * taillebloc + 3 * taillebloc / 2), taillebloc, self.map),
    ]
    self.placer_points()  # Note la liste de tous les points de la map initialement
    self.creer_fruits()  # Crée 4 pacgommes et 2 fruits

  def creation_map(self, cartes): 
    """
    Méthode permettant de créer la carte de jeu à partir d'un fichier texte. Elle choisit une carte      aléatoire parmi les 10 dispos et la met en forme sous forme de liste de chaines de caractères

    Parameters : 
    ------
    cartes(str) : nom du fichier texte contenant la carte de jeu

    Returns : 
    ------
    None
    """
    
    self.map = []
    numero = random.randint(0, 9)
    with open(cartes, "r") as fichier:
      i = 0
      rows = fichier.readlines()
      # NE GARDE QUE LES 32 LIGNES DE LA CARTE CHOISIE
      for row in rows:
        if i >= numero * 32 and i <= numero * 32 + 32:
          if row != '\n':
            self.map.append(row[:-1] + "|")
        i += 1

  def placer_points(self):
    """
    Méthode permettant de placer les points de la carte de jeu sur la map.
    
    Returns : 
    ------
    None
    """
    self.points_restants = []
    # PLACE UN POINT POUR CHAQUE POSITION NOTEE "." DANS LA LISTE DE LA CARTE
    for i in range(len(self.map) - 1):
      row = []
      for j in range(len(self.map[0]) - 1):
        if self.map[i][j] == ".":
          if (i, j) != (29, 14):
            row.append(j)
      self.points_restants.append(row)

  def creer_fruits(self):
    """
    Méthode permettant de créer 4 pacgommes et 2 fruits.

    Returns : 
    ------
    None
    """
    
    liste = []
    for i in range(4): # Crée 4 pacgommes
      pacgomme = Fruits("pacgomme", self.map, self.taillebloc)
      liste.append(pacgomme)
    for i in range(2): # Crée 2 fruits
      fruit = Fruits("fruit", self.map, self.taillebloc)
      liste.append(fruit)
    self.fruits = liste

  def addfruits(self): 
    """
    Méthode permettant de remettre le nombre de fruits (non-pacgommes) à 2 sur la carte.

    Returns : 
    ------
    None
    """
    for i in range(2):
      if self.fruits[i + 4] == 0:
        self.fruits[i + 4] = Fruits("fruit", self.map, self.taillebloc)

  def update(self):  
    """
    Méthode permettant de déplacer chaque personnage un nombre de fois correspondant à sa vitesse.

    Returns : 
    ------
    None
    """
    pacman = self.personnages[0]
    for perso in self.personnages:
      if isinstance(perso, Pacman):
        for i in range(perso.vitesse):
          perso.deplacement(self.map)
      elif isinstance(perso, Fantome):
        for i in range(perso.vitesse):
          perso.deplacement(pacman.position, self.taillebloc, self.map,
                            pacman.orientation, self.personnages[1].position)

  def replacer_persos(self):  
    """
    Méthode permettant de replacer chaque personnage à sa position initiale lorsque Pacman a recolté     tous les points et qu'un changement de map a donc lieu

    Returns : 
    ------
    None
    """
    self.personnages[0].position = (14 * self.taillebloc +
                                    3 * self.taillebloc / 2,
                                    29 * self.taillebloc +
                                    3 * self.taillebloc / 2)
    for fantome in self.personnages[1:]:
      fantome.replacement()
