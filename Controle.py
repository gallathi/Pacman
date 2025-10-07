from math import *
from Jeu import Jeu
from Utils import Utils
import time
import tkinter as tk
import pygame


class Controle():
    """Classe qui gère les interactions avec le joueur (difficulté, touches pressées) ainsi que les collisions"""

    __slots__ = ["modele", "taillebloc", "difficulte"]

    def __init__(self, taillebloc):
        self.taillebloc = taillebloc
        # CREE L'INSTANCE DU MODELE DE JEU ET DES PERSOS
        self.modele = Jeu(self.taillebloc)

        # REGLE LA DIFFICULTE ET FAIT LES CHANGEMENTS QUI Y SONT LIES
        self.difficulte = self.set_difficulte()

    def set_difficulte(self):
        """
        Méthode qui permet de choisir le niveau de difficulté du jeu et programme le jeu
pour réaliser les modfifications attendues selon la difficulté choisie.
    
        Returns
        -------
        dif(int) : Difficulté du jeu
    
        """
        print("1 = 3 fantômes + 3 vies")
        print("2 = 4 fantômes + 3 vies")
        print("3 = 4 fantômes + 1 vie")
        dif = int(input("Choisissez la difficulté (1, 2 ou 3) : "))
        if dif == 1:
            self.modele.personnages.pop(3)  # Pinky n'est plus en jeu
        elif dif == 3:
            self.modele.personnages[0].vies = 1  # Le joueur n'a qu'une vie
        return dif

    def se_touche(self, pacman, perso2):
        """
        Méthode qui vérifie si Pacman rentre en collision avec un fruit ou un fantôme.

        Parameters:
        ----------
        pacman (objet) : Objet de la classe Pacman
        perso2 (object/int) : Objet de la classe Fantome ou Fruit ou un entier dans le cas où l'objet est mangé

        Returns
        -------
        dif(int) : Difficulté du jeu

        """
        if perso2 == 0:  # Si perso2 est un fruit mangé, Pacman ne peut plus le toucher
            return False
        else:  # Sinon on regarde si Pacman et le perso2 sont à une distance de moins d'un bloc
            x2, y2 = perso2.position
            x1, y1 = pacman.position
            distance = sqrt((x2 - x1)**2 + (y2 - y1)**2)
            if distance < pacman.taillebloc - 1:
                return True
            else:
                return False

    def collisions(self):
        """
        Méthode qui réalise l'ensemble des actions attendues lors d'une collision entre pacman et un autre élément.

        Returns
        -------
        mort (bool) : True si Pacman est mort, False sinon
        point (int) : Nombre de points gagnés par le fruit mangé
        map_finie (bool) : True si Pacman a mangé tous es points, False sinon
        compteur (int) : Compteur des différents timers de réapparition ou de durée de pacgomme

        """
        mort = False  # Pacman s'est-il fait attraper ?
        point = (0, 0)  # Pacman a-t-il gobé un point ?
        map_finie = False  # Pacman a-t-il mangé tous les points ?
        compteur = [0, 0, 0, 0, 0,
                    0]  # Doit-on lancer des timers de fruits/pacgommes ?
        pacman = self.modele.personnages[0]
        for i in range(len(self.modele.personnages) - 1):
            fantome = self.modele.personnages[i + 1]
            # SI PACMAN TOUCHE UN FANTOME SANS PACGOMME, IL MEURT
            if not fantome.mort and self.se_touche(pacman, fantome):
                if not self.modele.personnages[0].etat:
                    mort = True
                else:  # Sinon, il mange le fantôme qui réapparaitra 4 secondes plus tard
                    fantome.mort = True
                    compteur[i + 2] = 4

                    # SON DE PACMAN MANGEANT LE FANTOME
                    son = pygame.mixer.Sound("son/ghost.ogg")
                    son.play()
                    son.set_volume(0.4)

        # ON NOTE LA POSITION DE PACMAN
        Xpac, Ypac = floor(pacman.position[0] / self.taillebloc) - 1, floor(
            pacman.position[1] / self.taillebloc) - 1

        # ON REGARDE CHAQUE POINT DE LA LIGNE DE PACMAN
        row = self.modele.points_restants[Ypac]
        for indiceX in range(len(row)):
            if indiceX < len(row) and row[indiceX] == Xpac:
                # QUAND PACMAN TOUCHE LE POINT, IL GAGNE 1 DE SCORE
                self.modele.score += 1
                point = (row[indiceX], Ypac)
                self.modele.points_restants[Ypac].pop(indiceX)
                # S'IL N'Y A PLUS DE POINTS SUR LA LIGNE, ON VERIFIE QUE PACMAN N'A PAS DEJA MANGE TOUTES LES LIGNES (DANS CE CAS, IL A MANGE TOUS LES POINTS DE LA CARTE)
                if self.modele.points_restants[Ypac] == []:
                    map_finie = True
                    i = 0
                    while map_finie and i < len(self.modele.points_restants):
                        if self.modele.points_restants[i] != []:
                            map_finie = False
                        i += 1

        # ON REGARDE SI CHAQUE FRUIT TOUCHE PACMAN
        for i in range(len(self.modele.fruits)):
            fruit = self.modele.fruits[i]
            if self.se_touche(pacman, fruit):
                self.modele.score += fruit.score  # On ajoute le score du fruit au score total
                self.modele.fruits[i] = 0  # On supprime le fruit

                # ON RECUPERE LA DUREE DES TIMERS DE RESPAWN ET DE PACGOMME
                compteur[0], compteur[1] = fruit.disparition()

                # S'IL A MANGE UNE PACGOMME, LES FANTOMES SONT AFFAIBLIS ET LUI RENFORCE
                if compteur[1] > 0:
                    for perso in self.modele.personnages:
                        perso.etat = True
        return (mort, point, map_finie, compteur)

    def orientation(self, event):
        """
        Méthode qui récupère la touche appuyée et la note comme future orientation, celle-ci changera si Pacman n'a pas de mur dans cette direction. 

        Parameters:
        ----------
        event(event) : Evènement correspondant à la touche appuyée

        Returns
        -------
        None

        """
        orientation = event.keysym  # Récupération de la touche appuyée
        x, y = self.modele.personnages[0].position
        if orientation == "Up":
            self.modele.personnages[0].future_orientation = "N"
        elif orientation == "Right":
            self.modele.personnages[0].future_orientation = "E"
        elif orientation == "Left":
            self.modele.personnages[0].future_orientation = "W"
        elif orientation == "Down":
            self.modele.personnages[0].future_orientation = "S"
