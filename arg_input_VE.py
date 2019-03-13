import numpy as np
import pandas as pd
import scipy.stats as stats
import math
from API_import import API_import_conso_commune

# Création de 2 listes associant à chaque VE entrant/sortant une puissance de charge (supposée identique au domicile et au travail)
# En fonction de :
#     Matrice des puissances possibles et de leur répartition : puissances [[3,7,18],[0.45,0.45,0.1]] # kW,%
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_ent [1]

def puissance_charge(puissances,  nombre_VE_sort, nombre_VE_ent):
    #Repartition de la puissance de charge
    repart_puissances_sort = np.random.choice(puissances[0], nombre_VE_sort, p=puissances[1]).tolist()
    repart_puissances_ent = np.random.choice(puissances[0], nombre_VE_ent, p=puissances[1]).tolist()


    return repart_puissances_sort, repart_puissances_ent


#Il s'agit ici de créer une liste contenant tous les trajets quotidiens individuels dans le périmètre du poste source.
#Nous créons une liste contenant les flux entrant (qui inclut les flux entre communes raccordées au même poste), 
#et une autre contenant les flux sortant

def trajets_quotidiens(poste, taux_equipement):
    
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
    nb_VE_sort = math.floor(nb_foyer*taux_equipement)
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

def dist_domicile_travail(flux, nombre_VE_sort, nombre_VE_ent):
    # Donnees flux
    flux_sortant_lisse = pd.DataFrame(flux['flux_sortant'])
    flux_entrant_lisse = pd.DataFrame(flux['flux_entrant'])

    #Distances parcourues par les VE
    dist_parc_VE_sort = flux_sortant_lisse.sample(n=nombre_VE_sort)[0].tolist()
    dist_parc_VE_ent = flux_entrant_lisse.sample(n=nombre_VE_ent)[0].tolist()

    return dist_parc_VE_sort, dist_parc_VE_ent

def dist_parcourue(flux, nombre_VE_sort, nombre_VE_ent, heures, h_aller, h_retour):
    # Donnees flux
    flux_sortant_lisse = pd.DataFrame(flux['flux_sortant'])
    flux_entrant_lisse = pd.DataFrame(flux['flux_entrant'])

    #Distances parcourues par les VE
    dist_aller_VE_sort = flux_sortant_lisse.sample(n=nombre_VE_sort)[0].tolist()
    dist_aller_VE_ent = flux_entrant_lisse.sample(n=nombre_VE_ent)[0].tolist()

    # Index des heures interdites
    index_trajet = heures.index[heures.isin([h_aller, h_retour])]

    #Creation des matrices de distances parcourues
    dist_parc_sort = pd.DataFrame(np.zeros((len(heures), nombre_VE_sort)))
    dist_parc_ent = pd.DataFrame(np.zeros((len(heures), nombre_VE_ent)))

    dist_parc_sort.iloc[index_trajet,:] = dist_aller_VE_sort
    dist_parc_ent.iloc[index_trajet,:] = dist_aller_VE_ent

    return dist_parc_sort, dist_parc_ent



# Création de la liste des heures de la plage de temps considérée
# En fonction de :
#     La courbe de charge

def horodate_list(courbe_de_charge):
    # Liste des heures
    heures = courbe_de_charge['horodate'].str.extract('T([^+]*)')[0]
    return heures


# Creation de listes contenant le SOC des VE entrant et sortant
# En fonction de :
#     Bornes des SOC de charge initiale : SOC_min, SOC_max [%]
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_en [1]

def seuil_recharge(SOC_min, SOC_max, nombre_VE_sort, nombre_VE_ent):
    SOC_sort = np.random.uniform(SOC_min, SOC_max, nombre_VE_sort).tolist()
    SOC_ent = np.random.uniform(SOC_min, SOC_max, nombre_VE_ent).tolist()

    return SOC_sort, SOC_ent

# Création de 2 listes associant à chaque VE entrant/sortant une taille de batterie
# En fonction de :
#     Matrice des tailles possibles et de leur répartition : tailles[[40,18,33,70],[0.5,0.1,0.2,0.2]] # kWh,%
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_ent [1]

def taille_batterie(tailles,  nombre_VE_sort, nombre_VE_ent):
    # Repartition des tailles des batteries
    repart_taille_sort = np.random.choice(tailles[0], nombre_VE_sort, p=tailles[1]).tolist()
    repart_taille_ent = np.random.choice(tailles[0], nombre_VE_ent, p=tailles[1]).tolist()

    return repart_taille_sort, repart_taille_ent

# Calcul des nombres de VE entrant/sortant
# En fonction du :
#     Taux de penetration des VE [%]

def nombre_VE(penetration_VE, flux):
    # Donnees flux
    flux_sortant_lisse = flux['flux_sortant']
    flux_entrant_lisse = flux['flux_entrant']

    # Nombres de VE
    nombre_VE_sort = math.floor(len(flux_sortant_lisse) * penetration_VE)  # sortant
    nombre_VE_ent = math.floor(len(flux_entrant_lisse) * penetration_VE)  # entrant

    return nombre_VE_sort, nombre_VE_ent
    
# Creation de listes contenant le SOC initial des VE entrant et sortant
# En fonction de :
#     Bornes des SOC de charge initiale : SOC_min, SOC_max [%]
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_en [1]

def ene_init(SOC_min, SOC_max, nombre_VE_sort, nombre_VE_ent):
    SOC_init_sort = np.random.uniform(SOC_min, SOC_max, nombre_VE_sort).tolist()
    SOC_init_ent = np.random.uniform(SOC_min, SOC_max, nombre_VE_ent).tolist()

    return SOC_init_sort, SOC_init_ent