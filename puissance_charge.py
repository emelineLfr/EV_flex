import numpy as np

# Création de 2 listes associant à chaque VE entrant/sortant une puissance de charge (supposée identique au domicile et au travail)
# En fonction de :
#     Matrice des puissances possibles et de leur répartition : puissances [[3,7,18],[0.45,0.45,0.1]] # kW,%
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_ent [1]

def puissance_charge(puissances,  nombre_VE_sort, nombre_VE_ent):
    #Repartition de la puissance de charge
    repart_puissances_sort = np.random.choice(puissances[0], nombre_VE_sort, p=puissances[1]).tolist()
    repart_puissances_ent = np.random.choice(puissances[0], nombre_VE_ent, p=puissances[1]).tolist()


    return repart_puissances_sort, repart_puissances_ent