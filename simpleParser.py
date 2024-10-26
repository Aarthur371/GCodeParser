# TODO :
# modifier traitement du G92 pour ne pas faire de d�placement quand on envoie G92


import re 

#---------------------------VARIABLES---------------------------#



#---------------------------FONCTIONS---------------------------#

def extraire_donnees_fichier(fichier):
    ''' Parcourt le fichier donne et recupere les valeurs des positions X,Y,Z et celle de l'extrudeur E
    Commandes traitees : G0,G1,G28,G92
    fichier : chemin relatif vers le fichier contenant le gcode
    return : liste des positions successives [X,Y,Z], elements = None si pas de deplacement dans une direction'''

    donnees = []
    lastPos = [0,0,0,0] #liste pour sauvegarder les derni�res positions sur chaque axe
    # Ouvrir le fichier pour la lecture
    with open(fichier, 'r') as f:
        lignes = f.readlines()

        # Parcourir chaque ligne du fichier
        for ligne in lignes:
            # Traduit la commande G28 = "home all axis" en une position [0,0,0]
            if ligne.startswith('G28'):
                donnees.append([0.0,0.0,0.0,None])
            # V�rifier si la ligne commence par G1 ou G0 = "linear move"
            elif ligne.startswith(('G1','G0','G92')):
                # Utiliser une regex pour trouver les valeurs X,Y,Z,E
                x = re.search(r'X([-\d.]+)', ligne)
                y = re.search(r'Y([-\d.]+)', ligne)
                z = re.search(r'Z([-\d.]+)', ligne)
                e = re.search(r'E([-\d.]+)', ligne)

                # Extraire les valeurs et les mettre dans une liste, mettre None si une valeur est manquante
                valeurs = [
                    float(x.group(1)) if x else lastPos[0],
                    float(y.group(1)) if y else lastPos[1],
                    float(z.group(1)) if z else lastPos[2],
                    float(e.group(1)) if e else lastPos[3]
                ]
                # V�rifie que l'on a au moins une instruction de d�placement en X, Y, Z ou E (exclue les commandes Feedrate)
                if any (val is not 0 for val in valeurs):
                    # Ajouter cette ligne de valeurs � la liste de donn�es
                    donnees.append(valeurs)

    return donnees


def calculDirectionDepl(donnees):
    '''Creation du vecteur contenant les valeurs de deplacement en X,Y,Z entre 2 positions
    donnees : liste des positions absolues [X,Y,Z]
    return : liste des deplacement relatifs [X,Y,Z] '''

    directions = []
    for i in range (1,len(donnees)):
            # Calculer les diff�rences si la ligne contient X ou Y ou Z
            if donnees[i][0] is not None or donnees[i][1] is not None or donnees[i][2] is not None:
                # Si pas de position pr�c�dente, on remonte en arri�re jusqu'� la derni�re position connue
                gobackX, gobackY, gobackZ = 0
                # Parcourir la liste � l'envers
                for i in range(len(donnees) - 1, -1, -1):
                    if donnees[i][0] is not None:
                        posLastX = i #indice de la derni�re position non vide en X
                    if donnees[i][1] is not None:
                        posLastY = i #indice de la derni�re position non vide en Y
                    if donnees[i][2] is not None:
                        posLastZ = i #indice de la derni�re position non vide en Z
                    if (posLastX!=0 and posLastY!=0 and posLastZ!=0):
                        break  # Arr�ter la boucle d�s que la derni�re valeur non vide est trouv�e pour chaque coordonn�es
                
                # Si on a une position pr�c�dente X,Y,Z, on calcule la diff�rence (arrondie � 5 d�cimales)
                diffX = round(donnees[i][0] - donnees[posLastX][0],5)
                diffY = round(donnees[i][1] - donnees[posLastY][1],5)
                diffZ = round(donnees[i][1] - donnees[posLastZ][1],5)
                directions.append([diffX,diffY,0])
    return directions

#-----------------------BOUCLE PRINCIPALE-------------------------#