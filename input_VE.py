# Renvoie les arguments necessaires à la generation de la courbe de charge des VE
from arg_input_VE import trajets_quotidiens, dist_domicile_travail, horodate_list, nombre_VE, seuil_recharge, puissance_charge, taille_batterie
from S1 import S1
from S2 import S2
from S3 import S3

def input_VE(poste, courbe_de_charge, penetration, tailles, puissances, SOC_min, SOC_max, taux_base, taux_pos, scenario):
    
    # Dates et heures
    heures = horodate_list(courbe_de_charge)

    # Flotte de VE
    flux = trajets_quotidiens(poste)
    nombre_VE_sort, nombre_VE_ent = nombre_VE(penetration, flux) #nombre de VE (selon taux de pénétration)
    SOC_sort, SOC_ent = seuil_recharge(SOC_min, SOC_max, nombre_VE_sort, nombre_VE_ent) #% recharge initiale batterie
    dist_parc_VE_sort, dist_parc_VE_ent = dist_domicile_travail(flux, nombre_VE_sort, nombre_VE_ent) #liste des distances parcourues par chaque VE)
    repart_puissances_sort, repart_puissances_ent = puissance_charge(puissances, nombre_VE_sort, nombre_VE_ent) #chaque individu se voit attribuer une puissance
    repart_taille_sort, repart_taille_ent = taille_batterie(tailles, nombre_VE_sort, nombre_VE_ent) #repartition de la taille des batterie pour chaque individu

    # Débuts de charge et interdictions
    T_debut_sort, T_debut_ent, plage_sort, plage_ent, dist_parc_sort, dist_parc_ent = vars('S'+scenario)(flux, heures, nombre_VE_sort, nombre_VE_ent, taux_base, taux_pos)
    
    return {'SOC_sort' : SOC_sort, 
            'SOC_ent' : SOC_ent, 
            'dist_parc_VE_sort' : dist_parc_VE_sort,
            'dist_parc_VE_ent' : dist_parc_VE_ent, 
            'repart_taille_sort' : repart_taille_sort, 
            'repart_taille_ent' : repart_taille_ent, 
            'repart_puissances_sort' : repart_puissances_sort, 
            'repart_puissances_ent' : repart_puissances_ent, 
            'T_debut_sort' : T_debut_sort, 
            'T_debut_ent' : T_debut_ent, 
            'plage_sort' : plage_sort, 
            'plage_ent' : plage_ent,
            'dist_parc_sort' : dist_parc_sort, 
            'dist_parc_ent' : dist_parc_ent
            }