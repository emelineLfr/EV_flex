import numpy as np 

#une petite fonction pour detecter si la batterie est à plus de 80% de sa charge, et mettre un coefficient adapté 
#ici charge deux fois plus lentement si supérieur à 80%
def sup80(vecteur, cd1, cd2, seuil ):
    l = len(vecteur)
    coeff = np.ones(l)
    for i in range(l) :
        if (vecteur[i]>seuil) :
            coeff[i] = cd2
        else : 
            coeff[i] = cd1
    return(coeff)
            
            
def matrice_charge_VE(trajet_parcouru,recharge_disponible,pourcent_min_batterie,taille_batterie,puissance_charge,heure_charge,conso_km = 0.1):
    nb_vehicules = np.shape(trajet_parcouru)[0]
    nb_pas_temps = np.shape(trajet_parcouru)[1]
    
    #matrice des distances parcourues
    trajet_parcouru = np.zeros((nb_vehicules,nb_pas_temps))
    
    #matrice des energies
    energie_batterie = np.zeros((nb_vehicules,nb_pas_temps))
    
    #matrice des charges
    en_charge = np.zeros((nb_vehicules,nb_pas_temps))
    
    #etat initial des batteries (lundi 0h00)
    vecteur_energie_debut = 10*np.random.randn(nb_vehicules) + 50
    for i in range (nb_vehicules) :
        if vecteur_energie_debut[i] >100 :
            vecteur_energie_debut[i] = 100
    
    vecteur_energie_debut = np.transpose(vecteur_energie_debut)
    #initialisation de la première colonne avec un vecteur gaussien 
    energie_batterie[:,0] = vecteur_energie_debut
    #initialisation de la première colonne avec des charges aléatoires
    en_charge[:,0] = np.random.randint(2,size =(1,nb_vehicules))
    
    ###################################################################################################
    ###################################################################################################
    ###################################################################################################
    
    for i in range (1, nb_pas_temps):
        
    #     print('energie_batterie en % avant trajet ',i, energie_batterie)
    #     print('taille de la batterie', taille_batterie )
        
        
        # calcul des vitesses de charge : la vitesse est divisée par deux si la batterie est chargée à 80% ou plus
        coeff_vitesse_charge = sup80(energie_batterie[:,i-1],0.5,0.25,80)
        
    #     print('coeff_vitesse_charge : ',i, coeff_vitesse_charge)
        
        #conversion des pourcentages en energie
        energie_batterie[:,i] = np.multiply(energie_batterie[:,i-1],
                                            np.divide(taille_batterie,nb_vehicules*[100]))
        
    #     print('energie_batterie en kWh avant trajet ', i , energie_batterie )#attention seule la derniere valeur est en kwh à cette etape, les autres c'est en %
        
        
        
        
        
        #energie apportée par la charge pendant le pas horaire précédent si il y en a une
        energie_charge = np.multiply(np.multiply(en_charge[:,i-1],
                                                 puissance_charge),
                                     coeff_vitesse_charge)
        
    #     print('energie apportée par la charge ',i, energie_charge)
        
        #energie effectivement apportée par la charge
        energie_charge = np.multiply(energie_charge,en_charge[:,i-1])
        
    #     print('seuil de charge pour ce vehicule', pourcent_min_batterie)
    #     print('y a t il une charge en cours ?',i,en_charge[:,i-1])
    #     print('energie apportée effectivement par la charge ',i, energie_charge)
        
        #energie de la batterie après charge
        energie_batterie[:,i] = np.add(energie_batterie[:,i], energie_charge)
        
    #     print('energie_batterie après charge précédente',i, energie_batterie)
        
        
        #enlève l'énergie consommée pendant un trajet sur le pas horaire précédent 
        energie_batterie[:,i] = np.subtract(energie_batterie[:,i],
                                            np.multiply(trajet_parcouru[:,i-1],(nb_vehicules*[conso_km])))
        
    #     print('energie_batterie après trajet ',i, energie_batterie)
        
        
        
        
    
        #remise des énergies batteries en pourcentage
        energie_batterie[:,i] = np.multiply(np.divide(energie_batterie[:,i],taille_batterie), [100]*nb_vehicules)
        
    #     print('energie_batterie après trajet et charge précédente en % avant ajustement ',i, energie_batterie)
        
        #remplacement des valeurs de charge supérieures à 100% par 100%
        for j in range (0,nb_vehicules):
            if (energie_batterie[j][i]>100):
                energie_batterie[j][i]=100
                
    #     print('energie_batterie après trajet et charge précédente en % ',i, energie_batterie)
        
        
        #construction de la matrice "en charge"
        for k in range (nb_vehicules) :
            if (((( (en_charge[k][i-1] == 1) & (energie_batterie[k][i]!=100)) 
                  or (energie_batterie[k][i] < pourcent_min_batterie[k]) 
                  or heure_charge[k][i] == 1 )) & (recharge_disponible[k][i] == 1)) :
                en_charge[k][i] = 1
    #             print(k,' charge au prochain pas de temps')
            else :
                en_charge[k][i] = 0
    #             print(k,' pas de charge au prochain pas de temps')
        
        
        
    #     print('matrice en_charge : ',i, en_charge)
        
    #     print('_______________________________________________________')
    #     print('_______________________________________________________')
    #     print('_______________________________________________________')
    
    



###################################################################################################
###################################################################################################
###################################################################################################



    #courbe de charge des VE

    charge = np.zeros(nb_pas_temps)

    for i in range (nb_pas_temps) : 
        charge[i] = np.sum(np.multiply(en_charge[:,i],puissance_charge))
        
    #plt.plot(charge)
    
    return(charge)