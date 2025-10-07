import time
import tkinter as tk
from math import *
from Controle import Controle
from Pacman import Pacman
from Fruits import Fruits
import tkinter.font as tkFont
import sys
import pygame


class FenetreGraphique(tk.Tk):
  """Classe gérant l'interface graphique du jeu"""
  __slots__ = [
      "controle", "canvas", "taillebloc", "pacman_images", "ghost_images",
      "images_actives", "label_score", "label_vies", "fruit_image", "timer",
      "label_temps", "compteur", "images_fruits", "game_over_image",
      "audio_file"
  ]

  def __init__(self):
    # INITIALISATION D'ATTRIBUTS
    super().__init__()
    self.title("PACMAN")
    self.taillebloc = 16
    self.configure(background="black")
    self.compteur = [0, 0, 0, 0, 0, 0]
    self.images_fruits = []
    self.images_actives = dict()
    self.charger_images()
    self.timer = (0, 0)

    # INITIALISATION DU CONTROLE, DU MODELE DE JEU ET DES PERSOS
    self.controle = Controle(self.taillebloc)

    # MISE EN PLACE DE L'AFFICHAGE
    self.widgets()  # Crée le canvas et les boutons/labels
    self.mise_en_place()  # Affiche les murs, les points et les persos

    # INITIALISATION DE LA MUSIQUE DE FOND (trouvée sur chatgpt)
    pygame.init()
    pygame.mixer.init()
    pygame.mixer.music.load("son/audio.ogg")
    pygame.mixer.music.set_volume(0.1)

  def charger_images(self):
    """
    Méthode permettant de charger les images et donc de créer la banque d'images du jeu.

    Returns : 
    ------
    None
    """
    self.pacman_images = {
        "N": tk.PhotoImage(file="images/pacman-upp.png"),
        "S": tk.PhotoImage(file="images/pacman-downn.png"),
        "W": tk.PhotoImage(file="images/pacman-gauchee.png"),
        "E": tk.PhotoImage(file="images/pacman-droitee.png")
    }
    self.ghost_images = {
        "clyde": tk.PhotoImage(file="images/CLYDE.png"),
        "inky": tk.PhotoImage(file="images/INKY.png"),
        "pinky": tk.PhotoImage(file="images/PINKY.png"),
        "blinky": tk.PhotoImage(file="images/BLINKY.png"),
        "vulnerable": tk.PhotoImage(file="images/vulnerable_ghost.png")
    }
    self.fruit_images = [
        tk.PhotoImage(file="images/strawberry.png"),
        tk.PhotoImage(file="images/bleu.png")
    ]
    self.game_over_image = tk.PhotoImage(file="images/over.png")

  def widgets(self):
    """
    Méthode permettant de créer les widgets de la fenêtre graphique.

    Returns : 
    ------
    None
    """

    # GESTION DE L'ORIENTATION DE PACMAN
    super().bind("<Key>", self.controle.orientation)

    # LABEL DE SCORE
    self.label_score = tk.Label(self,
                                text=f"SCORE : {self.controle.modele.score}",
                                background="black",
                                fg="white",
                                borderwidth=2,
                                font=tkFont.Font(family='DejaVu Sans Mono',
                                                 size=18))
    self.label_score.grid(row=1, column=2)

    # LABEL DU TIMER
    self.label_temps = tk.Label(self,
                                text=f"TIMER : {self.timer[1]}",
                                background="black",
                                fg="white",
                                borderwidth=2,
                                font=tkFont.Font(family='DejaVu Sans Mono',
                                                 size=18))
    self.label_temps.grid(row=1, column=1)

    # LABEL DES VIES DE PACMAN
    self.label_vies = tk.Label(
        self,
        text=f"VIES : {self.controle.modele.personnages[0].vies}",
        background="black",
        fg="white",
        borderwidth=2,
        font=tkFont.Font(family='DejaVu Sans Mono', size=18))
    self.label_vies.grid(row=1, column=0)

    # DECALAGE D'UNE LIGNE DU GRID (ESTHETIQUE)
    label = tk.Label(self, background="black")
    label.grid(row=2, column=0)

    # BOUTON START
    start = tk.Button(self,
                      text="START",
                      background="yellow",
                      borderwidth=1,
                      highlightbackground="red",
                      font=tkFont.Font(family='DejaVu Sans Mono', size=10))
    start.grid(column=1)
    start.bind(
        "<Button-1>", lambda event, arg=start: self.demarrer(event, arg)
    )  # Envoie son id comme argument pour pouvoir se débinder après le premier clic

    # CREATION DU CANVAS
    self.canvas = tk.Canvas(self,
                            width=500,
                            height=550,
                            background="black",
                            highlightthickness=0)
    self.canvas.grid(column=1)

  def mise_en_place(self):
    """
    Méthode permettant d'afficher les murs, les points et les personnages sur la fenêtre graphique.

    Returns : 
    ------
    None
    """

    # Affichage des murs, points et persos
    for i in range(len(self.controle.modele.map) - 1):
      for j in range(len(self.controle.modele.map[0]) - 1):
        if self.controle.modele.map[i][
            j] == "|":  # Pour chaque point de la carte qui est représenté par |, on le dessine à sa position
          self.dessiner_mur(i, j)
    self.afficher_points()  # Afficher tous les points de la carte
    self.afficher_fruits()  # Affiche les fruits
    if 'Pacman' not in self.images_actives.keys(
    ):  # Quand on a fini une map et qu'on en recrée une, il n'est pas nécessaire d'afficher les persos à nouveau
      self.afficher_personnages()

  def demarrer(self, event, button):
    """
    Méthode permettant de lancer la boucle du jeu et donc de démarrer la partie.

    Parameters :
    ------
    button (int) : id du bouton start

    Returns : 
    ------
    None
    """

    button.unbind(
        '<Button-1>'
    )  # Empêche de démarrer plusieurs fois le jeu (ce qui augmenterait la vitesse de Pacman)
    self.timer = (time.time(), 0)  # Initialisation du timer à 0
    pygame.mixer.music.play(-1)  # Lance la musique
    self.boucle()  # Lance la boucle de jeu

  def boucle(self):
    """
    Méthode permettant d'assurer une boucle de jeu en garantissant les effets visuels, les déplacements des personnages et les fonctionnalités du jeu nécessaires.

    Returns : 
    ------
    None
    """

    self.actualiser_compteurs_et_score(
    )  # Update le timer et les compteurs de respawn de fruits, de fantômes et d'effet de pacgomme
    self.effacer_personnages(
    )  # Efface les images de Pacman, des fantômes et les fruits
    self.controle.modele.update(
    )  # Actualise les positions de Pacman et des fantômes
    self.effets_des_collisions(
    )  # Adapter l'affichage si Pacman a mangé un point/fruit/fantôme (quand sous pacgomme) ou se fait tuer par un fantôme
    self.afficher_personnages(
    )  # Redessiner Pacman et les fantômes à leurs nouvelles positions
    self.after(
        40, self.boucle
    )  #  Relancer cette fonction en boucle tant que Pacman n'est pas mort

  def actualiser_compteurs_et_score(self):
    """
    Méthode permettant d'actualiser les différents compteurs du jeu (temps, pacgomme, réapparition des fruits) et le score du joueur.

    Returns : 
    ------
    None
    """
    # ACTUALISATION DU SCORE
    self.label_score.config(text="SCORE : " + str(self.controle.modele.score))

    # ACTUALISATION DU TIMER ET DES COMPTEURS DE TEMPS DE PACGOMME ET RESPAWN DE FRUITS
    if time.time() - 1 > self.timer[0]:
      self.timer = (time.time(), self.timer[1] + 1)
      self.label_temps.config(text="TIMER : " + str(self.timer[1]))
      for i in range(len(self.compteur)
                     ):  # Chaque seconde, on diminue tous les compteurs de 1
        self.compteur[i] -= 1
      if self.compteur[
          0] == 0:  # Si le compteur de fruits est à 0, on crée un nouveau fruit
        self.controle.modele.addfruits()  # Respawn de fruit
        self.afficher_fruits()  # Affichage du nouveau fruit
      if self.compteur[1] == 0:  # Fin de la pacgomme
        for perso in self.controle.modele.personnages:
          perso.etat = False  # Désactivation des états de vulnérabilité des fantômes
      for j in range(
          len(self.compteur) -
          2):  # Si le compteur d'un fantôme mort est à 0, il est repositionné
        if self.compteur[j + 2] == 0:
          self.controle.modele.personnages[j + 1].mort = False
          self.controle.modele.personnages[j + 1].replacement()

  def effets_des_collisions(self):
    """
    Méthode permettant de gérer entièrement les effets de collisions au sein de la map.

    Returns : 
    ------
    None
    """
    mort, point, map_finie, compteur = self.controle.collisions(
    )  # Pacman a-t-il été touché par un fantôme ? Quel point a été mangé ? Pacman a-t-il mangé tous les points ? Faut-il initialiser des compteurs de pacgomme ou fruit ?

    # GESTION DE LA PERTE DE VIE
    if mort:
      self.controle.modele.personnages[0].vies += -1
      if self.controle.modele.personnages[0].vies == 0:
        # SON DE MORT DE PACMAN
        son = pygame.mixer.Sound("son/mort.mp3")
        son.play()
        son.set_volume(0.5)
        self.game_over()
        self.label_vies.config(text="VIES : 0")
      elif self.controle.modele.personnages[0].vies > 0:
        # SON DE MORT DE PACMAN
        son = pygame.mixer.Sound("son/mort.mp3")
        son.play()
        son.set_volume(0.5)
        self.label_vies.config(text="VIES : " +
                               str(self.controle.modele.personnages[0].vies))
        self.respawn()

    # GESTION DU POINT MANGE
    if point != (0, 0):
      self.effacer_point(point)

    # GESTION DE LA FIN DE LA MAP
    if map_finie:  # Si tous les points ont été mangés, on change de carte en gardant le score et les vies
      self.nouvelle_map()

    # ACTUALISATION DES FRUITS MANGES ET INITIALISATION DES COMPTEURS DE PACGOMME ET RESPAWN DE FRUITS
    for i in range(len(self.compteur)):
      if compteur[i] != 0:
        self.compteur[i] = compteur[i]
        if i <= 2:  # Si le compteur de fruits n'est pas à 0, c'est qu'un fruit a été créé donc on l'affiche
          self.afficher_fruits()

  def nouvelle_map(self):
    """
    Méthode permettant de créer une nouvelle map de jeu lorsque Pacman a récolté tous les points.
    
    Returns : 
    ------
    None
    """

    # CREATION DE LA MAP, DES POINTS ET REPOSITIONNEMENT DES PERSOS
    self.controle.modele.creation_map("Maps.txt")
    self.controle.modele.placer_points()
    self.controle.modele.replacer_persos()

    # EFFACAGE DU CANVAS
    self.canvas.create_rectangle(self.taillebloc,
                                 self.taillebloc,
                                 self.taillebloc * 29,
                                 self.taillebloc * 32,
                                 fill="black",
                                 outline='black')
    # CREER DE NOUVEAUX FRUITS ET AFFICHAGES DES MURS ET POINTS
    self.controle.modele.creer_fruits()
    self.mise_en_place()

  def game_over(self):
    """
    Méthode permettant de récupérer et afficher l'image GAME OVER lorsque           l'utilisateur a perdu la partie.
    
    Returns : 
    ------
    None
    """
    self.canvas.create_image(
        250, 280, anchor=tk.CENTER,
        image=self.game_over_image)  # Affichage de l'image de game over
    self.canvas.after(3000, self.close_window)
    pygame.mixer.music.stop()  # Arrêt de la musique à la fin du jeu

  def close_window(self):
    """
    Méthode permettant de détruire le canvas et fermer la fenêtre principale.

    Returns : 
    ------
    None
    """
    F.destroy()  # Fermeture du canvas
    sys.exit()  # Fermeture du programme python

  def respawn(self):
    """
    Méthode permettant de faire réapparaitre Pacman lorsque celui-ci perd une       vie. Pacman se replace après un freeze/gel de 3 secondes

    Returns : 
    ------
    None
    """
    time.sleep(1)  # Pause pour que le joueur voie bien ce qu'il se passe
    self.controle.modele.replacer_persos()

  def dessiner_mur(self, Y, X):
    """
    Méthode permettant de dessiner un bloc de mur selon sa position.

    Parameters :
    ------
    Y (int) : position en Y de la case
    X (int) : position en X de la case
    
    Returns : 
    ------
    None
    """
    # Dessine un bloc de mur selon sa case
    # PASSAGE DES COORDONNEES LISTE AUX COORDONNEES EN PIXEL
    x0, y0, x1, y1 = (X + 1) * self.taillebloc, (Y + 1) * self.taillebloc, (
        X + 2) * self.taillebloc, (Y + 2) * self.taillebloc

    # CREATION DU CARRE BLEU QUI REPRESENTE LE MUR
    self.canvas.create_rectangle(x0, y0, x1, y1, fill="blue", outline='black')

  def afficher_points(self):
    """
    Méthode permettant d'afficher les points qui n'ont pas encore été récolté       par Pacman

    Returns : 
    ------
    None
    """
    rows = self.controle.modele.points_restants
    for i in range(len(rows)):
      for j in rows[i]:
        Y, X = i, j
        self.dessiner_point(Y, X)

  def dessiner_point(self, Y, X):
    """
    Méthode permettant de dessiner un point selon sa position.

    Parameters :
    ------
    Y (int) : position en Y de la case
    X (int) : position en X de la case

    Returns : 
    ------
    None
    """
    # PASSAGE DES COORDONNEES LISTE AUX COORDONNEES EN PIXEL
    x0, y0, x1, y1 = (X + 1.3) * self.taillebloc, (
        Y + 1.3) * self.taillebloc, (X + 1.7) * self.taillebloc, (
            Y + 1.7) * self.taillebloc

    # CREATION DU ROND JAUNE QUI REPRESENTE LE POINT
    self.canvas.create_oval(x0, y0, x1, y1, fill="yellow", outline='black')

  def effacer_point(self, point):
    """
    Méthode permettant d'effacer les points recoltés par Pacman.

    Parameters :
    ------
    point (tuple) : position du point à effacer

    Returns : 
    ------
    None
    """
    # PASSAGE DES COORDONNEES LISTE AUX COORDONNEES EN PIXEL
    X, Y = point
    x0, y0, x1, y1 = (X + 1.3) * self.taillebloc, (
        Y + 1.3) * self.taillebloc, (X + 1.7) * self.taillebloc, (
            Y + 1.7) * self.taillebloc
    # EFFACAGE DU ROND QUI REPRESENTAIT LE POINT
    self.canvas.create_oval(x0, y0, x1, y1, fill="black", outline='black')

  def afficher_personnages(self):
    """
    Méthode permettant d'afficher les personnages sur la fenêtre graphique.

    Returns : 
    ------
    None
    """

    # Affichage des persos
    for perso in self.controle.modele.personnages:
      # CREE L'IMAGE DE PACMAN A SES COORDONNEES
      if isinstance(perso, Pacman):
        img = self.pacman_images[perso.orientation]
        self.images_actives['Pacman'] = self.canvas.create_image(
            perso.position[0], perso.position[1], anchor=tk.CENTER, image=img)
      else:
        # CREE L'IMAGE D'UN FANTOME (VULNERABLE OU NON) A SES COORDONNEES S'IL            EST VIVANT
        if not perso.mort:
          if perso.etat:
            img = self.ghost_images["vulnerable"]
          else:
            img = self.ghost_images[perso.nom]
          self.images_actives[perso.nom] = self.canvas.create_image(
              perso.position[0],
              perso.position[1],
              anchor=tk.CENTER,
              image=img)

  def effacer_personnages(self):
    """
    Méthode permettant d'effacer les personnages de la fenêtre graphique avant      de les placer à leur nouvelle position.

    Returns : 
    ------
    None
    """
    for key in self.images_actives.keys():
      img = self.images_actives[key]
      self.canvas.delete(img)

  def afficher_fruits(self):
    """
    Méthode permettant d'actualiser l'affichage de tous les fruits (fraise et       pacgommes).
    
    Returns : 
    ------
    None
    """
    # EFFACE TOUS LES FRUITS AFFICHES
    for i in range(len(self.images_fruits)):
      self.canvas.delete(self.images_fruits[0])
      self.images_fruits.pop(0)

    # NE REAFFICHE QUE LES FRUITS/PACGOMMES RESTANTS ET AJOUTES
    for pacgomme in self.controle.modele.fruits[:4]:
      if pacgomme != 0:
        self.images_fruits.append(
            self.canvas.create_image(pacgomme.position,
                                     image=self.fruit_images[1]))
    for fruit in self.controle.modele.fruits[4:]:
      if fruit != 0:
        img = self.fruit_images
        self.images_fruits.append(
            self.canvas.create_image(fruit.position,
                                     image=self.fruit_images[0]))


F = FenetreGraphique()
F.mainloop()
pygame.mixer.music.stop(
)  # Arrêt de la musique quand on ferme la fenêtre graphique manuellement avant la fin de la partie
