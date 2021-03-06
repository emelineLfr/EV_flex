# Renvoie les arguments necessaires à la generation de la courbe de charge des VE
from arg_input_VE import *
from S1 import S1
from S2 import S2
from S3 import S3

def input_VE(poste, taux_equipement, courbe_de_charge, penetration, tailles, puissances, SOC_min, SOC_max, SOC_init_min, SOC_init_max, taux_base, taux_pos, scenario):
    
    # Dates et heures
    heures = horodate_list(courbe_de_charge)

    # Flotte de VE
    flux = trajets_quotidiens(poste, taux_equipement)
    nombre_VE_sort, nombre_VE_ent = nombre_VE(penetration, flux) #nombre de VE (selon taux de pénétration)
    SOC_sort, SOC_ent = seuil_recharge(SOC_min, SOC_max, nombre_VE_sort, nombre_VE_ent) #% recharge initiale batterie
    SOC_init_sort, SOC_init_ent = ene_init(SOC_init_min, SOC_init_max, nombre_VE_sort, nombre_VE_ent) #% renvoie le SOC initial des VE
    dist_parc_VE_sort, dist_parc_VE_ent = dist_domicile_travail(flux, nombre_VE_sort, nombre_VE_ent) #liste des distances parcourues par chaque VE)
    repart_puissances_sort, repart_puissances_ent = puissance_charge(puissances, nombre_VE_sort, nombre_VE_ent) #chaque individu se voit attribuer une puissance
    repart_taille_sort, repart_taille_ent = taille_batterie(tailles, nombre_VE_sort, nombre_VE_ent) #repartition de la taille des batterie pour chaque individu
    
    # Débuts de charge et interdictions
    function = {'Name': 'S'+ str(scenario), 'Arg': '(flux, heures, nombre_VE_sort, nombre_VE_ent, taux_base, taux_pos)'}
    T_debut_sort, T_debut_ent, plage_sort, plage_ent, dist_parc_sort, dist_parc_ent = eval(function['Name'] + function['Arg'])
    
    return {'SOC_sort' : SOC_sort, 
            'SOC_ent' : SOC_ent, 
            'dist_parc_VE_sort' : dist_parc_VE_sort,
            'dist_parc_VE_ent' : dist_parc_VE_ent, 
            'repart_taille_sort' : repart_taille_sort, 
            'repart_taille_ent' : repart_taille_ent, 
            'repart_puissance_sort' : repart_puissances_sort, 
            'repart_puissance_ent' : repart_puissances_ent, 
            'T_debut_sort' : T_debut_sort, 
            'T_debut_ent' : T_debut_ent, 
            'plage_sort' : plage_sort, 
            'plage_ent' : plage_ent,
            'dist_parc_sort' : dist_parc_sort, 
            'dist_parc_ent' : dist_parc_ent,
            'SOC_init_sort' : SOC_init_sort, 
            'SOC_init_ent': SOC_init_ent
            }