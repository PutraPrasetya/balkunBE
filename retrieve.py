import numpy as np
import pandas as pd

def knn_func(newCluster):
    # Pembobotan
    bobot = [10, 8, 10, 7, 4, 6, 7]
    jumlah_bobot = sum(bobot)
    total_rows = len(newCluster.index)

    xdaerah = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,0] != newCluster.iloc[j,0]:
            xdaerah.append(0)
        elif newCluster.iloc[-1,0] == newCluster.iloc[j,0]:
            xdaerah.append(bobot[0])

    xtempat = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,1] != newCluster.iloc[j,1]:
            xtempat.append(0)
        elif newCluster.iloc[-1,1] == newCluster.iloc[j,1]:
            xtempat.append(bobot[1])

    xkategori = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,2] != newCluster.iloc[j,2]:
            xkategori.append(0)
        elif newCluster.iloc[-1,2] == newCluster.iloc[j,2]:
            xkategori.append(bobot[2])

    xjenis = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,3] != newCluster.iloc[j,3]:
            xjenis.append(0)
        elif newCluster.iloc[-1,3] == newCluster.iloc[j,3]:
            xjenis.append(bobot[3])

    xrasa = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,4] != newCluster.iloc[j,4]:
            xrasa.append(0)
        elif newCluster.iloc[-1,4] == newCluster.iloc[j,4]:
            xrasa.append(bobot[4])

    xharga = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,5] != newCluster.iloc[j,5]:
            xharga.append(0)
        elif newCluster.iloc[-1,5] == newCluster.iloc[j,5]:
            xharga.append(bobot[5])

    xrating = []
    for j in range(total_rows-1):
        if newCluster.iloc[-1,6] != newCluster.iloc[j,6]:
            xrating.append(0)
        elif newCluster.iloc[-1,6] == newCluster.iloc[j,6]:
            xrating.append(bobot[6])

    #Perhitungan Similarity
    similarity = []
    for j in range (total_rows-1):
        similarity.append((xdaerah[j] + xtempat[j] + xkategori[j] + xjenis[j] + xrasa[j] + xharga[j] + xrating[j]) / jumlah_bobot * 100)
    similarity = np.array(similarity)

    index = []
    for j in range (total_rows-1):
        index.append(newCluster.index[j])
    index = np.array(index)

    dataframe_similarity=pd.DataFrame(index, columns=['Index']) 
    dataframe_similarity['Nilai_Similarity'] = similarity

    treshold_resto = dataframe_similarity.loc[(dataframe_similarity.Nilai_Similarity >= 70)]
    treshold_resto = treshold_resto.sort_values('Nilai_Similarity',ascending=False)

    return treshold_resto