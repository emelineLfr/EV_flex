import numpy as np

# Creation de listes contenant le SOC des VE entrant et sortant
# En fonction de :
#     Bornes des SOC de charge initiale : SOC_min, SOC_max [%]
#     Nombre de VE entrant et sortant : nombre_VE_sort, nombre_VE_en [1]

def seuil_recharge(SOC_min, SOC_max, nombre_VE_sort, nombre_VE_ent):
    SOC_sort = np.random.uniform(SOC_min, SOC_max, nombre_VE_sort).tolist()
    SOC_ent = np.random.uniform(SOC_min, SOC_max, nombre_VE_ent).tolist()

    return SOC_sort, SOC_ent