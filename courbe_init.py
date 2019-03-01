import pandas as pd
import numpy as np
import requests
import json
from API_import_coef import API_import_coef
from API_import_conso_commune import API_import_conso_commune

#Creation d'une courbe de charge estimee au niveau d'un transformateur d'un poste selectionne
#En fonction des donnees annuelles de consommation electriques des communes rattachees
#Et d'une estimation de la repartition des profils de consommateurs sur ces communes
#En supposant que la puissance est equitablement repartie entre les transformateurs du poste

def courbe_init(poste, nb_transfo, date_debut, date_fin, res, pro, ent, secteur_res, secteur_pro, secteur_ent):
    
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
        conso_commune = API_import_conso_commune(str(code_commune)) #dictionnaire contenant les consommations electriques de chaque secteur en 2017 pour la commune donnee
        if conso_commune: #Si il y a des donnees pour la commune donnee ... 
            for secteur in secteurs: 
                if 'conso_totale_'+secteur+'_mwh' in conso_commune:
                    vars()['conso_totale_'+secteur+'_mwh'].append(conso_commune['conso_totale_'+secteur+'_mwh'])

    #chargement des coefficients
    for profil in profils: 
        coef = API_import_coef(date_debut, date_fin, profil[0]) 
        if not coef.empty : 
            vars()['coef_'+profil[0]] = coef
        
        #Si le profil n'existe pas, il faut le supprimer et reequilibrer les poids relatifs
        else :
            print('Un des profils consommateur est erronne')
            for categorie in ['res','pro','ent']:
                if profil in vars()[categorie]: 
                    vars()[categorie].remove(profil) #On supprime le profil errone de la categorie
                    for PROFIL_ in vars()[categorie]:
                        PROFIL_[1] += profil[1]/(len(res)-1) #On repartit le poids du profil errone sur les autres


    #### PUISSANCE MOYENNE ABSORBEE PAR PROFIL ####
    for categorie in ['res','pro','ent']:
        vars()['P_'+categorie] = 0
        for secteur in vars()['secteur_'+categorie] :
            vars()['P_'+categorie] += sum(vars()['conso_totale_'+secteur+'_mwh'])/(nb_pas*nb_transfo)
        for profil in vars()[categorie] :
            vars()['P_'+profil[0]] = profil[1]*vars()['P_'+categorie]

    #### CONSTRUCTION COURBE CHARGE AU NIVEAU DU TRANSFO ####
    courbe_de_charge = pd.DataFrame()
    courbe_de_charge['horodate'] =  vars()['coef_'+res[0][0]]['horodate']

    courbe_de_charge['P'] = 0
    for profil in profils : 
        courbe_de_charge['P'] = courbe_de_charge['P'] + vars()['P_'+profil[0]]*vars()['coef_'+profil[0]]['coefficient_ajuste']

    return courbe_de_charge