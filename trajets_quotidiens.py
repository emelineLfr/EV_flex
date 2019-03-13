import numpy as np
import pandas as pd
import scipy.stats as stats
import math
from API_import import API_import_conso_commune


def trajets_quotidiens_EL_v2(poste, penetration):
    
    #DETERMINATION DU NOMBRE DE VE SORTANTS : 
    #On determine le nombre de foyers dans les communes rattachees au poste source considere
    #On calcule le nombre de voitures a partir du taux d'equipement des menages (2015, INSEE : 80.9% dont 46.7% avec 1 et 34.2% avec 2 ou plus)
    #pour obtenir le nombre de VE sortants
    #Le nombre de foyers est egal au nombre d'habitants divise par la taille moyenne des menages français (2015, INSEE : 2.23)
    
    #Extraction des codes communes des communes rattachees au poste source
    postes_sources = pd.read_csv('allocation_postes_sources.csv', sep=';')
    communes = postes_sources.loc[postes_sources['Poste_source']==poste]['Code_Commune'].tolist()
    
    #Calcul du nombre de foyers
    nb_foyer = 0
    taille_foyer = 2.23 #
    for code_commune in communes:
        conso_commune = API_import_conso_commune(str(code_commune))
        if conso_commune:
            if 'nombre_d_habitants' in conso_commune:
                nb_foyer += conso_commune['nombre_d_habitants']/taille_foyer   
    
    #NOMBRE DE VE REEL CALCULE
    
    #Extraction des flux de VE de l'enquete de mobilite    
    table_flux = pd.read_csv('tableau_flux.csv', sep=';')
    flux_sortant = table_flux.loc[table_flux['PS_Depart'] == poste].sort_values(by=['Distance'])
    flux_sortant = flux_sortant[flux_sortant.PS_Depart != flux_sortant.PS_Arrivee]
    flux_entrant = table_flux.loc[table_flux['PS_Arrivee'] == poste].sort_values(by=['Distance'])
    
    #Nombres VE initiaux (d'apres l'etude de mobilite)
    nb_VE_sort_init = flux_sortant['Flux'].sum()
    nb_VE_ent_init = flux_entrant['Flux'].sum()
    
    #Nombres VE target (en considérant que les proportions sont conservées)
    nb_VE_sort = math.floor(nb_foyer*penetration)
    taux_ent = nb_VE_ent_init/nb_VE_sort_init
    nb_VE_ent = math.floor(nb_VE_sort*taux_ent)
       
    #Nouveaux flux sortant (sur la base du total correspondant au nombre reel calcule de vehicules)
    flux_sortant['Flux'] = flux_sortant['Flux']*math.floor(nb_VE_sort/nb_VE_sort_init)
    flux_entrant['Flux'] = flux_entrant['Flux']*math.floor(nb_VE_ent/nb_VE_ent_init)

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



# Création de 2 listes associant à chaque VE entrant/sortant une distance domicile-travail
# En fonction de :
#     Indentifiant du poste source de départ/arrivée : poste (1 à 2234)
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_ent [1]


