import pandas as pd
import numpy as np
import requests
import json

# Fonction permettant d'importer les coefficients des profils sur une plage temporelle choisie

def API_import_coef(date_debut, date_fin, profil):
    url = 'https://data.enedis.fr/api/records/1.0/search/?dataset=coefficients-des-profils&q=sous_profil%3A%22'+profil+'%22+AND+horodate%3A+%5B'+date_debut+'T00%3A00%3A00+TO+'+ date_fin +'T23%3A59%3A59%5D&rows=10000&sort=horodate&facet=horodate&facet=sous_profil&facet=categorie'
    r = requests.get(url)
    dic = r.json()

    if not dic['records']:
        return pd.DataFrame()
    
    else :
        f = lambda x : x['fields']['horodate'] 
        g = lambda x : x['fields']['coefficient_ajuste'] 
        horodate = [f(x) for x in dic['records']] #liste des horodates pour le profil donne, sur la plage temporelle selectionne
        coefficient_ajuste = [g(x) for x in dic['records']] #liste des coefficients ajustes correspondant au profil et a la plage temporelle donnee
        
        #Creation d'un dataframe associant les coefficients du profil a leur horodate
        coef = pd.DataFrame()
        coef['horodate']=horodate
        coef['coefficient_ajuste']=coefficient_ajuste
        return coef
