import pandas as pd
import numpy as np
import math
import scipy.stats as stats
from arg_input_VE import dist_parcourue


# Creation de la matrice des heures de debut de charge et des interdictions de charge imposees par le Scenario 1 (Recharge le soir)
# En fonction du :
#     Nombre de VE entrant/sortant [1]
#     Matrice des temps : heures
#     Matrice des distances parcourures

def S1(flux, heures, nombre_VE_sort, nombre_VE_ent, taux_base, taux_pos):
    # MATRICES T DEBUTS
    # Initialisation
    T_debut_sort = pd.DataFrame(np.ones((len(heures), 1)))
    T_debut_ent = pd.DataFrame(np.ones((len(heures), 1)))

    # Debuts recharges
    inf_sort = ['18:00:00']
    mid_sort = ['19:00:00']
    sup_sort = ['20:00:00']

    inf_ent = ['08:00:00']
    mid_ent = ['10:00:00']
    sup_ent = ['12:00:00']

    # Index des heures possibles
    dif_inf_sort = heures.index[heures == inf_sort[0]][0] - heures.index[heures == mid_sort[0]][0]
    dif_sup_sort = heures.index[heures == sup_sort[0]][0] - heures.index[heures == mid_sort[0]][0]

    dif_inf_ent = heures.index[heures == inf_ent[0]][0] - heures.index[heures == mid_ent[0]][0]
    dif_sup_ent = heures.index[heures == sup_ent[0]][0] - heures.index[heures == mid_ent[0]][0]

    # Distribution gaussienne des Tdebut
    mu_sort = heures.index[heures == mid_sort[0]][0]
    sigma_sort = 3
    debut_sort = stats.truncnorm((dif_inf_sort) / sigma_sort, (dif_sup_sort) / sigma_sort, loc=mu_sort,
                                 scale=sigma_sort)
    distri_sort = [math.floor(x) for x in debut_sort.rvs(nombre_VE_sort).tolist()]

    mu_ent = heures.index[heures == mid_ent[0]][0]
    sigma_ent = 3
    debut_ent = stats.truncnorm((dif_inf_ent) / sigma_ent, (dif_sup_ent) / sigma_ent, loc=mu_ent, scale=sigma_ent)
    distri_ent = [math.floor(x) for x in debut_ent.rvs(nombre_VE_ent).tolist()]

    # Creation matrice Tdebut
    for ve in range(nombre_VE_sort):
        Td_sort = heures.loc[distri_sort[ve]]
        Td_sort_index = [int(x) for x in heures.isin([Td_sort])]
        T_debut_sort[ve] = np.transpose(np.array([Td_sort_index]))  # Output sortant

    for ve in range(nombre_VE_ent):
        Td_ent = heures.loc[distri_ent[ve]]
        Td_ent_index = [int(x) for x in heures.isin([Td_ent])]
        T_debut_ent[ve] = np.transpose(np.array([Td_ent_index]))  # Output sortant

    # MATRICES INTERDICTIONS DE CHARGE
    # Initialisation
    plage_sort = pd.DataFrame(np.ones((len(heures), nombre_VE_sort)))
    plage_ent = pd.DataFrame(np.zeros((len(heures), nombre_VE_ent)))

    # Bande interdite
    inf_sort = ['06:00:00']
    sup_sort = ['17:00:00']

    # Bande autorisee
    inf_ent = ['07:30:00']
    sup_ent = ['16:30:00']

    # Index des heures interdites
    index_inf_sort = heures.index[heures == inf_sort[0]]
    index_sup_sort = heures.index[heures == sup_sort[0]]

    index_inf_ent = heures.index[heures == inf_ent[0]]
    index_sup_ent = heures.index[heures == sup_ent[0]]

    # Ecritures de zeros/uns sur les heures interdites/autorisees
    for i in range(len(index_inf_sort)):
        plage_sort.loc[index_inf_sort[i]:index_sup_sort[i], :] = 0

    for i in range(len(index_inf_ent)):
        plage_ent.loc[index_inf_ent[i]:index_sup_ent[i], :] = 1

    # MATRICES STANCES PARCOURUES
    h_aller = '08:00:00'
    h_retour = '18:00:00'

    dist_parc_sort, dist_parc_ent = dist_parcourue(flux, nombre_VE_sort, nombre_VE_ent, heures, h_aller, h_retour)

    return T_debut_sort, T_debut_ent, plage_sort, plage_ent, dist_parc_sort, dist_parc_ent