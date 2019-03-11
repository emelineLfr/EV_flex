import numpy as np 

#une petite fonction pour detecter si la batterie est à plus de 80% de sa charge, et mettre un coefficient adapté 
#ici charge deux fois plus lentement si supérieur à 80%
def sup(vecteur, cd1, cd2, seuil ):
    l = len(vecteur)
    coeff = np.ones(l)
    for i in range(l) :
        if (vecteur[i]>seuil) :
            coeff[i] = cd2
        else : 
            coeff[i] = cd1
    return(coeff)
            

def matrice_charge_VE(trajet_parcouru, recharge_disponible, pourcent_min_batterie, taille_batterie, puissance_charge, heure_charge, vecteur_energie_debut, conso_km = 0.1):
    # Passage au format array
    trajet_parcouru = np.array(trajet_parcouru)
    recharge_disponible = np.array(recharge_disponible)
    pourcent_min_batterie = np.array(pourcent_min_batterie)
    taille_batterie = np.array(taille_batterie)
    puissance_charge = np.array(puissance_charge)
    heure_charge = np.array(heure_charge)
    vecteur_energie_debut = np.array(vecteur_energie_debut)
    
    # Dimensions
    nb_vehicules = np.shape(trajet_parcouru)[1]
    nb_pas_temps = np.shape(trajet_parcouru)[0]
    
    # Initialisation
    energie_batterie = np.zeros((nb_pas_temps, nb_vehicules)) # Energies stockées dans les batteries des VE
    en_charge = np.zeros((nb_pas_temps, nb_vehicules)) # Etat du véhicule (en charge = 1, pas en charge = 0)
    
    # Initialisation de la première ligne
    energie_batterie[0,:] = vecteur_energie_debut # Energie initiale %
    en_charge[0,:] = np.random.randint(2,size=(1,nb_vehicules)) # Etats de charge aléatoires
    
    # Construction des matrices 
    for i in range (1, nb_pas_temps):
        
        # Calcul des vitesses de charge : la vitesse est divisée par deux si la batterie est chargée à 80% ou plus
        coeff_vitesse_charge = sup(energie_batterie[i-1,:],0.5,0.25,0.8)
        
        # Energie au temps i = Energie (kWh) au temps i-1...
        energie_batterie[i,:] = np.multiply(energie_batterie[i-1,:], taille_batterie) 
        
        # ... + Energie apportée par la charge pendant le pas horaire précédent...
        energie_charge = np.multiply(np.multiply(en_charge[i-1,:], puissance_charge*0.5), coeff_vitesse_charge)
        energie_batterie[i,:] = np.add(energie_batterie[i,:], energie_charge)
        
        # ... - Energie consommée pendant un trajet sur le pas horaire précédent 
        energie_batterie[i,:] = np.subtract(energie_batterie[i,:], trajet_parcouru[i-1,:]*conso_km)
        
        # Remise des énergies batteries en % 
        energie_batterie[i,:] = np.divide(energie_batterie[i,:], taille_batterie)
        
        # Remplacement des valeurs de charge supérieures à 100% par 100%
        for j in range (nb_vehicules):
            if energie_batterie[i][j]>1:
                energie_batterie[i][j]=1

        # Construction de la matrice "en charge"
        for k in range (nb_vehicules) :
            if ((((en_charge[i-1][k] == 1) & (energie_batterie[i][k]<1)) or (energie_batterie[i][k] < pourcent_min_batterie[k]) or (heure_charge[i][k] == 1 )) & (recharge_disponible[i][k] == 1)):
                en_charge[i][k] = 1
            else:
                en_charge[i][k] = 0
        
    # Courbe de charge des VE
    charge = np.zeros((nb_pas_temps,1))
    charge = np.sum(np.multiply(en_charge,puissance_charge), axis= 1)*0.001 # Puissance résultante en MW

    return(charge)