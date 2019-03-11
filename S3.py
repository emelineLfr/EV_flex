import pandas as pd
import numpy as np
import math
import scipy.stats as stats
from arg_input_VE import dist_parcourue


# Creation de la matrice des heures de debut de charge et des interdictions imposees par le Scenario 3 (Recharge travail)
# En fonction du :
#     Nombre de VE entrant/sortant [1]
#     Taux de recharge travail possible
#     Matrice des temps : heures

def S3(flux, heures, nombre_VE_sort, nombre_VE_ent, taux_base, taux_pos):

# MATRICES DES T DEBUTS
    # Initialisation
    T_debut_sort = pd.DataFrame(np.ones((len(heures), 1)))
    T_debut_ent = pd.DataFrame(np.ones((len(heures), 1)))

    # Distinction recharge au travail possible VS impossible
    nombre_VE_sort_pos = math.floor(nombre_VE_sort * taux_pos)
    nombre_VE_sort_imp = nombre_VE_sort - nombre_VE_sort_pos
    id_VE_sort_pos = np.random.choice(np.arange(nombre_VE_sort), nombre_VE_sort_pos, replace=False).tolist()
    id_VE_sort_imp = [x for x in np.arange(nombre_VE_sort) if x not in id_VE_sort_pos]

    # Debuts recharges
    inf_sort_pos = ['09:00:00', '18:00:00']
    mid_sort_pos = ['10:00:00', '19:00:00']
    sup_sort_pos = ['11:00:00', '20:00:00']

    inf_sort_imp = ['18:00:00']
    mid_sort_imp = ['19:00:00']
    sup_sort_imp = ['20:00:00']

    inf_ent = ['08:00:00']
    mid_ent = ['10:00:00']
    sup_ent = ['12:00:00']

    # Index des heures possibles
    dif_inf_sort_pos = heures.index[heures.isin(inf_sort_pos)][0:len(inf_sort_pos)] - heures.index[heures.isin(mid_sort_pos)][0:len(mid_sort_pos)]
    dif_sup_sort_pos = heures.index[heures.isin(sup_sort_pos)][0:len(sup_sort_pos)] - heures.index[heures.isin(mid_sort_pos)][0:len(mid_sort_pos)]

    dif_inf_sort_imp = heures.index[heures.isin(inf_sort_imp)][0:len(inf_sort_imp)] - heures.index[heures.isin(mid_sort_imp)][0:len(mid_sort_imp)]
    dif_sup_sort_imp = heures.index[heures.isin(sup_sort_imp)][0:len(sup_sort_imp)] - heures.index[heures.isin(mid_sort_imp)][0:len(mid_sort_imp)]

    dif_inf_ent = heures.index[heures == inf_ent[0]][0] - heures.index[heures == mid_ent[0]][0]
    dif_sup_ent = heures.index[heures == sup_ent[0]][0] - heures.index[heures == mid_ent[0]][0]

    # Distribution gaussienne des Tdebut
    distri_sort_pos = np.ones((len(mid_sort_pos), nombre_VE_sort_pos))
    for h in range(len(mid_sort_pos)):
        mu_pos = heures.index[heures == mid_sort_pos[h]][0]
        sigma_pos = 3
        debut_sort_pos = stats.truncnorm((dif_inf_sort_pos[h]) / sigma_pos, (dif_sup_sort_pos[h]) / sigma_pos,
                                         loc=mu_pos, scale=sigma_pos)
        distri_sort_pos[h] = [math.floor(x) for x in debut_sort_pos.rvs(nombre_VE_sort_pos).tolist()]

    distri_sort_imp = np.ones((len(mid_sort_imp), nombre_VE_sort_imp))
    for h in range(len(mid_sort_imp)):
        mu_imp = heures.index[heures == mid_sort_imp[h]][0]
        sigma_imp = 3
        debut_sort_imp = stats.truncnorm((dif_inf_sort_imp[h]) / sigma_imp, (dif_sup_sort_imp[h]) / sigma_imp,
                                         loc=mu_imp, scale=sigma_imp)
        distri_sort_imp[h] = [math.floor(x) for x in debut_sort_imp.rvs(nombre_VE_sort_imp).tolist()]

    mu = heures.index[heures == mid_ent[0]][0]
    sigma = 3
    debut_ent = stats.truncnorm((dif_inf_ent) / sigma, (dif_sup_ent) / sigma, loc=mu, scale=sigma)
    distri_ent = [math.floor(x) for x in debut_ent.rvs(nombre_VE_ent).tolist()]

    # Creation matrice Tdebut
    for ve in range(nombre_VE_sort_pos):
        Td_sort = heures.loc[distri_sort_pos[:, ve]]
        Td_sort_index = [int(x) for x in heures.isin(Td_sort)]
        T_debut_sort[id_VE_sort_pos[ve]] = np.transpose(np.array([Td_sort_index]))

    for ve in range(nombre_VE_sort_imp):
        Td_sort = heures.loc[distri_sort_imp[:, ve]]
        Td_sort_index = [int(x) for x in heures.isin(Td_sort)]
        T_debut_sort[id_VE_sort_imp[ve]] = np.transpose(np.array([Td_sort_index]))

    T_debut_sort = T_debut_sort.reindex(sorted(T_debut_sort.columns), axis=1)  # Reordonne les colonnes selon ordre VE initial

    for ve in range(nombre_VE_ent):
        Td_ent = heures.loc[distri_ent[ve]]
        Td_ent_index = [int(x) for x in heures.isin([Td_ent])]
        T_debut_ent[ve] = np.transpose(np.array([Td_ent_index]))

# MATRICES DES INTERDICTIONS DE CHARGE

    # Initialisation
    plage_sort = pd.DataFrame(np.ones((len(heures), nombre_VE_sort)))
    plage_ent = pd.DataFrame(np.zeros((len(heures), nombre_VE_ent)))

    # Bandes interdites
    inf_sort_imp = ['06:00:00']
    sup_sort_imp = ['17:00:00']

    # Bande autorisee
    inf_ent = ['07:30:00']
    sup_ent = ['16:30:00']

    # Index des heures interdites
    index_inf_sort_imp = heures.index[heures == inf_sort_imp[0]]
    index_sup_sort_imp = heures.index[heures == sup_sort_imp[0]]

    index_inf_ent = heures.index[heures == inf_ent[0]]
    index_sup_ent = heures.index[heures == sup_ent[0]]

    # Ecritures de zeros/uns sur les heures interdites/autorisees
    for i in range(len(index_inf_sort_imp)):
        plage_sort.loc[index_inf_sort_imp[i]:index_sup_sort_imp[i], id_VE_sort_imp] = 0

    for i in range(len(index_inf_ent)):
        plage_ent.loc[index_inf_ent[i]:index_sup_ent[i], :] = 1

    # MATRICES STANCES PARCOURUES
    h_aller = '08:00:00'
    h_retour = '18:00:00'

    dist_parc_sort, dist_parc_ent = dist_parcourue(flux, nombre_VE_sort, nombre_VE_ent, heures, h_aller, h_retour)

    return T_debut_sort, T_debut_ent, plage_sort, plage_ent, dist_parc_sort, dist_parc_ent