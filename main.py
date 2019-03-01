import pandas as pd
import numpy as np
import requests
import json
import matplotlib.pyplot as plt
from API_import_coef import API_import_coef
from API_import_conso_commune import API_import_conso_commune
from courbe_init import courbe_init
from courbe_ENR import courbe_sol #, courbe_eol

#### PARAMETRES

poste = 2154 #index du poste source dans le fichier GPS_poste_source
nb_transfo = 3 #nombre de transformateurs du poste source
date_debut = '2019-01-07'
date_fin = '2019-01-13'
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

#Capacites renevoulables
#estimables par poste source grace aux donnees S3REnR
#https://www.rte-france.com/fr/article/les-schemas-regionaux-de-raccordement-au-reseau-des-energies-renouvelables-des-outils
capa_sol = 5 #MW
capa_eol = 10 #MW

#### COURBE DE CHARGE

courbe_initiale = courbe_init(poste, nb_transfo, date_debut, date_fin, res, pro, ent, secteur_res, secteur_pro, secteur_ent)
courbe_prod_sol = courbe_sol(date_debut,date_fin,capa_sol)

#### GRAPHE

fig = plt.figure()
plt.plot(courbe_initiale['horodate'], courbe_initiale['P'])
plt.xlabel('Date et heure')
plt.ylabel('Puissance (MW)')
plt.show()