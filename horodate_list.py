# Création de la liste des heures de la plage de temps considérée
# En fonction de :
#     La courbe de charge

def horodate_list(courbe_de_charge):
    # Liste des heures
    heures = courbe_de_charge['horodate'].str.extract('T([^+]*)')[0]
    return heures