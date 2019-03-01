#Il s'agit ici de créer une liste contenant tous les trajets quotidiens individuels dans le périmètre du poste source.
#Nous créons une liste contenant les flux entrant (qui inclut les flux entre communes raccordées au même poste), 
#et une autre contenant les flux sortant

import pandas as pd
import numpy as np
import scipy.stats as stats

def trajets_quotidiens(poste):
    
    table_flux = pd.read_csv('tableau_flux.csv', sep=';')

    flux_sortant = table_flux.loc[table_flux['PS_Depart'] == poste].sort_values(by=['Distance'])
    flux_sortant = flux_sortant[flux_sortant.PS_Depart != flux_sortant.PS_Arrivee]
    flux_entrant = table_flux.loc[table_flux['PS_Arrivee'] == poste].sort_values(by=['Distance'])

    #A ce stade, nous avons une liste indiquant le nombre d'individus qui se déplacent d'une mairie à une autre.
    #Nous voulons créer une liste qui simule les déplacements individuels.
    #50% des communes en France ont une superficie comprise entre 5 et 15 kmxkm. 
    #Par ailleurs les distances sont ici calculees a vol d'oiseau entre deux mairies
    #Nous choisissons donc de lisser les distances par une gaussienne tronquee entre +- 10km, 
    #sauf pour les distances entre mairies inferieures à 10km, ou la gaussienne sera tronquee a +- la distance entre les deux mairies. 

    flux_sortant_lisse = []
    flux_entrant_lisse = []

    for i in range (flux_sortant.shape[0]):
        flux = flux_sortant.iloc[i]['Flux']
        distance = flux_sortant.iloc[i]['Distance']
    
        if distance > 10:
            lower = distance-10
            upper = distance+10
            
        else : 
            lower = 0.5
            upper = distance*2
    
        mu = distance
        sigma = 5

        X = stats.truncnorm((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma)
        samples = X.rvs(flux).tolist()
        
        flux_sortant_lisse.extend(samples)

    for i in range (flux_entrant.shape[0]):
        flux = flux_entrant.iloc[i]['Flux']
        distance = flux_entrant.iloc[i]['Distance']
        
        if distance > 10:
            lower = distance-10
            upper = distance+10
            
        else : 
            lower = 0.5
            upper = distance*2
    
        mu = distance
        sigma = 5

        X = stats.truncnorm((lower-mu)/sigma,(upper-mu)/sigma,loc=mu,scale=sigma)
        samples = X.rvs(flux)
        
        flux_entrant_lisse.extend(samples)

    return {'flux_sortant': flux_sortant_lisse, 'flux_entrant': flux_entrant_lisse}



