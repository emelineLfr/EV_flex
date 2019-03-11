import pandas as pd
import numpy as np
import math
import scipy.stats as stats
from arg_input_VE import dist_parcourue


# Creation de la matrice des heures de debut de charge et des interdictions de charge imposees par le Scenario 2 (HP/HC)
# En fonction du :
#     Nombre de VE entrant/sortant [1]
#     Taux de forfait base
#     Matrice des temps : heures

def S2(flux, heures, nombre_VE_sort, nombre_VE_ent, taux_base, taux_pos):

# MATRICES DES T DEBUTS
    # Initialisation
    T_debut_sort = pd.DataFrame(np.ones((len(heures), 1)))
    T_debut_ent = pd.DataFrame(np.ones((len(heures), 1)))

    # Distinction base VS HPHC
    nombre_VE_sort_base = math.floor(nombre_VE_sort * taux_base)
    nombre_VE_sort_HPHC = nombre_VE_sort - nombre_VE_sort_base
    id_VE_sort_base = np.random.choice(np.arange(nombre_VE_sort), nombre_VE_sort_base, replace=False).tolist()
    id_VE_sort_HPHC = [x for x in np.arange(nombre_VE_sort) if x not in id_VE_sort_base]

    # Debuts recharges
    inf_sort_base = ['18:00:00']
    mid_sort_base = ['19:00:00']
    sup_sort_base = ['20:00:00']

    inf_sort_HPHC = ['21:00:00']
    mid_sort_HPHC = ['22:00:00']
    sup_sort_HPHC = ['23:00:00']

    inf_ent = ['08:00:00']
    mid_ent = ['10:00:00']
    sup_ent = ['12:00:00']

    # Index des heures possibles
    dif_inf_sort_base = heures.index[heures == inf_sort_base[0]][0] - heures.index[heures == mid_sort_base[0]][0]
    dif_sup_sort_base = heures.index[heures == sup_sort_base[0]][0] - heures.index[heures == mid_sort_base[0]][0]

    dif_inf_sort_HPHC = heures.index[heures == inf_sort_HPHC[0]][0] - heures.index[heures == mid_sort_HPHC[0]][0]
    dif_sup_sort_HPHC = heures.index[heures == sup_sort_HPHC[0]][0] - heures.index[heures == mid_sort_HPHC[0]][0]

    dif_inf_ent = heures.index[heures == inf_ent[0]][0] - heures.index[heures == mid_ent[0]][0]
    dif_sup_ent = heures.index[heures == sup_ent[0]][0] - heures.index[heures == mid_ent[0]][0]

    # Distribution gaussienne des Tdebut
    mu_base = heures.index[heures == mid_sort_base[0]][0]
    sigma_base = 3
    debut_sort_base = stats.truncnorm((dif_inf_sort_base) / sigma_base, (dif_sup_sort_base) / sigma_base, loc=mu_base,
                                  scale=sigma_base)
    distri_sort_base = [math.floor(x) for x in debut_sort_base.rvs(nombre_VE_sort_base).tolist()]

    mu_HPHC = heures.index[heures == mid_sort_HPHC[0]][0]
    sigma_HPHC = 3
    debut_sort_HPHC = stats.truncnorm((dif_inf_sort_HPHC) / sigma_HPHC, (dif_sup_sort_HPHC) / sigma_HPHC, loc=mu_HPHC,
                                  scale=sigma_HPHC)
    distri_sort_HPHC = [math.floor(x) for x in debut_sort_HPHC.rvs(nombre_VE_sort_HPHC).tolist()]

    mu = heures.index[heures == mid_ent[0]][0]
    sigma = 3
    debut_ent = stats.truncnorm((dif_inf_ent) / sigma, (dif_sup_ent) / sigma, loc=mu, scale=sigma)
    distri_ent = [math.floor(x) for x in debut_ent.rvs(nombre_VE_ent).tolist()]

    # Creation matrice Tdebut VE
    for ve in range(nombre_VE_sort_base):
        Td_sort = heures.loc[distri_sort_base[ve]]
        Td_sort_index = [int(x) for x in heures.isin([Td_sort])]
        T_debut_sort[id_VE_sort_base[ve]] = np.transpose(np.array([Td_sort_index]))

    for ve in range(nombre_VE_sort_HPHC):
        Td_sort = heures.loc[distri_sort_HPHC[ve]]
        Td_sort_index = [int(x) for x in heures.isin([Td_sort])]
        T_debut_sort[id_VE_sort_HPHC[ve]] = np.transpose(np.array([Td_sort_index]))

    T_debut_sort = T_debut_sort.reindex(sorted(T_debut_sort.columns), axis=1)  # Output sortant

    for ve in range(nombre_VE_ent):
        Td_ent = heures.loc[distri_ent[ve]]
        Td_ent_index = [int(x) for x in heures.isin([Td_ent])]
        T_debut_ent[ve] = np.transpose(np.array([Td_ent_index]))  # Output entrant

# MATRICES DES INTERDICTIONS DE CHARGE
    # Initialisation
    plage_sort = pd.DataFrame(np.ones((len(heures), nombre_VE_sort)))
    plage_ent = pd.DataFrame(np.zeros((len(heures), nombre_VE_ent)))

    # Bandes interdites
    inf_sort_base = ['06:00:00']
    sup_sort_base = ['17:00:00']

    inf_sort_HPHC = ['06:00:00']
    sup_sort_HPHC = ['20:00:00']

    # Bande autorisee
    inf_ent = ['07:30:00']
    sup_ent = ['16:30:00']

    # Index des heures interdites
    index_inf_sort_base = heures.index[heures == inf_sort_base[0]]
    index_sup_sort_base = heures.index[heures == sup_sort_base[0]]

    index_inf_sort_HPHC = heures.index[heures == inf_sort_HPHC[0]]
    index_sup_sort_HPHC = heures.index[heures == sup_sort_HPHC[0]]

    index_inf_ent = heures.index[heures == inf_ent[0]]
    index_sup_ent = heures.index[heures == sup_ent[0]]

    # Ecritures de zeros/uns sur les heures interdites/autorisees
    for i in range(len(index_inf_sort_base)):
        plage_sort.loc[index_inf_sort_base[i]:index_sup_sort_base[i],id_VE_sort_base] = 0

    for i in range(len(index_inf_sort_HPHC)):
        plage_sort.loc[index_inf_sort_HPHC[i]:index_sup_sort_HPHC[i],id_VE_sort_HPHC] = 0

    for i in range(len(index_inf_ent)):
        plage_ent.loc[index_inf_ent[i]:index_sup_ent[i], :] = 1

    # MATRICES STANCES PARCOURUES
    h_aller = '08:00:00'
    h_retour = '18:00:00'

    dist_parc_sort, dist_parc_ent = dist_parcourue(flux, nombre_VE_sort, nombre_VE_ent, heures, h_aller, h_retour)

    return T_debut_sort, T_debut_ent, plage_sort, plage_ent, dist_parc_sort, dist_parc_ent