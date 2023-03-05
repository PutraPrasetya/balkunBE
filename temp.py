# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from knn import knn_func
from clustering import cluster_kmeans


def CBR(mydb, daerah, tempat, kategori, jenis, rasa, harga, rating):

    query = "SELECT * FROM dataset_restoran"
    data = pd.read_sql(query, con=mydb)
    print(data)
    # mengelompokkan harga
    batas_bin = [0, 19999, 39999, 59999, 100000]
    kategori = ['10K', '30K', '50K', '>50K']
    data['range_harga'] = pd.cut(data['Harga'], bins=batas_bin, labels=kategori)

    # mengelompokkan rating
    batas_bin = [3, 4, 4.3, 4.6, 5]
    kategori = ['Cukup', ' Cukup Baik', 'Baik', 'Sangat Baik']
    data['range_rating'] = pd.cut(data['Rating'], bins=batas_bin, labels=kategori)

    # membentuk tabel baru
    old_case = ['Daerah', 'Tempat', 'Kategori', 'Jenis', 'Rasa', 'range_harga', 'range_rating']
    old_case = data[old_case]
    old_case.head()

    # Input Data
    new_Case = {
        'Daerah':[daerah],
        'Tempat':[tempat],
        'Kategori':[kategori],
        'Jenis':[jenis],
        'Rasa':[rasa],
        'range_harga':[harga],
        'range_rating':[rating]
    }
    new_case = pd.DataFrame(new_Case)

    # Merge Kasus Lama dan Baru
    mergeData = [old_case, new_case]
    mergeData = pd.concat(mergeData).reset_index(drop=True)

    # One Hot Encoding
    # Convert data lama kategrorikal menjadi numerik
    le=LabelEncoder()
    for i in mergeData.columns:
        mergeData[i]=le.fit_transform(mergeData[i])

    # Indexing dengan K-Means
    newCluster = cluster_kmeans(mergeData)
    total_rows = len(newCluster.index)

    # Similarity dengan K-Nearest Neighbor
    treshold_resto = knn_func(newCluster)

    # Revise & Reuse
    solusi = treshold_resto.Index
    solusi = np.array(solusi)
    data_list = []
    len_solution = len(treshold_resto)

    if len_solution == 0:
        #Jika tidak ada rekomendasi masuk ke revise
        print("Mohon maaf, tidak ada rekomendasi untuk restoran yang anda cari\nMohon menunggu pakar dalam mencari rekomendasi yang sesuai untuk anda")
        mycursor = mydb.cursor()
        revise_sql = "INSERT INTO revise (Daerah, Tempat, Kategori, Jenis, Rasa, Harga, Rating) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        revise_src = (daerah, tempat, kategori, jenis, rasa, harga, rating)
        mycursor.execute(revise_sql, revise_src)
        mydb.commit() 

    else:
        #masukan data ke hasil
        for i in range(min(5, max(1, len(solusi)))):
            data_list.append(data.loc[solusi[i]])
        result = pd.DataFrame(data_list)
