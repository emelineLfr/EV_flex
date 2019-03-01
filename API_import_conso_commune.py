import pandas as pd
import numpy as np
import requests
import json

# Fonction permettant d'importer les consommations electriques par secteur des communes en 2017

def API_import_conso_commune(code_commune):
    url = 'https://data.enedis.fr/api/records/1.0/search/?dataset=consommation-electrique-par-secteur-dactivite-commune&q=code_commune+%3A+'+code_commune+'+AND+annee+%3A+2017&rows=10'
    r = requests.get(url)
    dic = r.json()
    if not dic['records']: 
        return {}
    else :
        return dic['records'][0]['fields']