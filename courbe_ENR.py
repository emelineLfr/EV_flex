import pandas as pd
import numpy as np
import requests
import json
from API_import_coef import API_import_coef

def courbe_sol(date_debut,date_fin, capa_sol): 
    P_sol = capa_sol/4 #sur les courbes de coefficients Enedis, on voit un facteur 4 entre la puissance moyenne et la puissance max, peut être retrouve avec les heures d'ensoleillement journaliers. 
    coef_sol = API_import_coef(date_debut, date_fin, 'PRD3_BASE')
    courbe_sol = pd.DataFrame()
    courbe_sol['horodate'] = coef_sol['horodate']
    courbe_sol['P'] = coef_sol['coefficient_ajuste']*P_sol
    return coef_sol 

#def courbe_eol(date_debut,date_fin, capa_eol):
   