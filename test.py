import pandas as pd
import numpy as np
import requests
import json

def API_import_conso_commune(code_commune):
    url = 'https://data.enedis.fr/api/records/1.0/search/?dataset=consommation-electrique-par-secteur-dactivite-commune&q=code_commune+%3A+'+code_commune+'+AND+annee+%3A+2017&rows=10'
    r = requests.get(url)
    dic = r.json()
    if not dic['records']:
        return 'no_data'
    else :
        return dic['records'][0]['fields']

def API_import_coef(date_debut, date_fin, profil):
    url = 'https://data.enedis.fr/api/records/1.0/search/?dataset=coefficients-des-profils&q=sous_profil%3A%22'+profil+'%22+AND+horodate%3A+%5B'+date_debut+'T00%3A00%3A00+TO+'+ date_fin +'T23%3A59%3A59%5D&rows=10000&sort=horodate&facet=horodate&facet=sous_profil&facet=categorie'
    r = requests.get(url)
    dic = r.json()
    
    f = lambda x : x['fields']['horodate']
    g = lambda x : x['fields']['coefficient_ajuste']

    horodate = [f(x) for x in dic['records']]
    coefficient_ajuste = [g(x) for x in dic['records']]

    coef = pd.DataFrame()
    coef['horodate']=horodate
    coef['coefficient_ajuste']=coefficient_ajuste
    return coef


poste = 2154 #index du poste source dans le fichier GPS_poste_source
nb_transfo = 3 #nombre de transformateurs du poste source
date_debut = '2019-01-07'
date_fin = '2019-01-13'
saison = 'H' #H pour hiver, E pour été

#Choix du scénario 
scenario = 'scenario_1'

#Répartition des profils profils de consommateurs
res = [['RES1_BASE', 1], ['RES2_HP', 0], ['RES2_HC', 0]]
pro = [['PRO1_BASE', 1], ['PRO2_HP', 0], ['PRO2_HC',0]]
ent = [['ENT1_HP'+saison, 0.5], ['ENT1_HC'+saison, 0.5]]
profils = res + pro + ent

#Répartition des secteurs dans les trois catégories de profils
secteur_res = ['residentiel']
secteur_pro = ['professionnel', 'agriculture', 'secteur_non_affecte']
secteur_ent = ['industrie', 'tertiaire']

profils = res + pro + ent
secteurs = secteur_ent + secteur_pro + secteur_res
nb_pas = 8760 #nb de pas horaires par an

#### DONNEES ####
#Selection des communes associees au poste source selectionne
postes_sources = pd.read_csv('allocation_postes_sources.csv', sep=';')
communes = postes_sources.loc[postes_sources['Poste_source']==poste]['Code_Commune'].tolist()
   
#Chargement des consommations 2017 des communes raccordees au poste par secteur 
for secteur in secteurs :
    vars()['conso_totale_'+secteur+'_mwh'] = []

for code_commune in communes: 
    conso_commune = API_import_conso_commune(str(code_commune))
    if conso_commune != 'no_data':
        for secteur in secteurs: 
            if 'conso_totale_'+secteur+'_mwh' in conso_commune:
                vars()['conso_totale_'+secteur+'_mwh'].append(conso_commune['conso_totale_'+secteur+'_mwh'])

#chargement des coefficients
for profil in profils: 
    vars()['coef_'+profil[0]] = API_import_coef(date_debut, date_fin, profil[0])


### PUISSANCE MOYENNE ABSORBEE PAR PROFIL ####
#Consommation résidentielle 
P_res = 0
for secteur in secteur_res :
    P_res += sum(vars()['conso_totale_'+secteur+'_mwh'])/nb_pas
for profil in res :
    vars()['P_'+profil[0]] = profil[1]*P_res

#Consommation professionnelle
P_pro = 0
for secteur in secteur_pro :
    P_pro += sum(vars()['conso_totale_'+secteur+'_mwh'])/nb_pas
for profil in pro :
    vars()['P_'+profil[0]] = profil[1]*P_pro

#Consommation résidentielle 
P_ent = 0
for secteur in secteur_ent :
    P_ent += sum(vars()['conso_totale_'+secteur+'_mwh'])/nb_pas
for profil in ent :
    vars()['P_'+profil[0]] = profil[1]*P_ent

#### CONSTRUCTION COURBE CHARGE AU NIVEAU DU TRANSFO ####
courbe_de_charge = pd.DataFrame()
courbe_de_charge['horodate'] =  vars()['coef_'+res[0][0]]['horodate']

courbe_de_charge['P'] = 0
for profil in profils : 
   courbe_de_charge['P'] = courbe_de_charge['P'] + vars()['P_'+profil[0]]*vars()['coef_'+profil[0]]['coefficient_ajuste']/nb_transfo