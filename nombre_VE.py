import math

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