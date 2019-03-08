import numpy as np

# Création de 2 listes associant à chaque VE entrant/sortant une taille de batterie
# En fonction de :
#     Matrice des tailles possibles et de leur répartition : tailles[[40,18,33,70],[0.5,0.1,0.2,0.2]] # kWh,%
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_ent [1]

def taille_batterie(tailles,  nombre_VE_sort, nombre_VE_ent):
    # Repartition des tailles des batteries
    repart_taille_sort = np.random.choice(tailles[0], nombre_VE_sort, p=tailles[1]).tolist()
    repart_taille_ent = np.random.choice(tailles[0], nombre_VE_ent, p=tailles[1]).tolist()

    return repart_taille_sort, repart_taille_ent