import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from API_import import API_import_coef, API_import_conso_commune
from courbe_init import courbe_init
from arg_input_VE import *
from input_VE import input_VE
from matrice_charge_VE import *

#### PARAMETRES

#POSTE SOURCE ET ECOSYSTEME

poste = 2154 #index du poste source dans le fichier GPS_poste_source
nb_transfo = 3 #nombre de transformateurs du poste source
saison = 'H' #H pour hiver, E pour été

#Répartition des profils de consommateurs
#LA SOMME DES POIDS POUR CHAQUE CATEGORIE DOIT VALOIR 1
res = [['RES1_BASE', 0.2], ['RES11_BASE',0.1],['RES2_HP', 0.45], ['RES2_HC', 0.25]]
pro = [['PRO1_BASE', 0.5], ['PRO2_HP', 0.2], ['PRO2_HC',0.1],['PRO5_BASE',0.2]]
ent = [['ENT1_HP'+saison, 0.2], ['ENT1_HC'+saison, 0.05],['ENT3_HP'+saison, 0.65], ['ENT3_HC'+saison, 0.1]]

#Répartition des secteurs dans les trois catégories de profils
secteur_res = ['residentiel']
secteur_pro = ['professionnel', 'agriculture', 'secteur_non_affecte']
secteur_ent = ['industrie', 'tertiaire']

#CHOIX DU SCENARIO 
scenario = 1
date_debut = '2019-01-07'
date_fin = '2019-01-13'

#PARAMETRES DE LA FLOTTE VE
penetration = 0.1  # %taux de pénétration de véhicules électriques
SOC_min, SOC_max = 0.15, 0.9 # la tolérance à la décharge des individus est un vecteur aléatoire entre SOC_min et max
tailles = [[40,18,33,70],[0.5,0.1,0.2,0.2]] # kWh / % : Répartition des tailles de batteries au sein du parc de VE
puissances = [[3,7,18],[0.45,0.45,0.1]] # kW / % : Répartition des puissances de charges (une Pch associée à chaque individu )
taux_base = 0.6 # % : taux de personnes sur le forfait base (charge à domicile)
taux_pos = 0.4 # % : Peuvent se recharger sur le lieu de travail 




#### COURBE DE CHARGE

courbe_de_charge = courbe_init(poste, nb_transfo, date_debut, date_fin, res, pro, ent, secteur_res, secteur_pro, secteur_ent)


#### GRAPHE

#fig = plt.figure()
#plt.plot(courbe_de_charge['horodate'], courbe_de_charge['P'])
#plt.xlabel('Date et heure')
#plt.ylabel('Puissance (MW)')
#plt.show()

#### INPUT COURBE DES VE
inputVE = input_VE(poste, courbe_de_charge, penetration, tailles, puissances, SOC_min, SOC_max, taux_base, taux_pos, scenario)