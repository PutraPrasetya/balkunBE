# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
import math
from retrieve import knn_func

# memanggil database
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="zetyaa",
  password="12345",
  database="cbr_restoran"
)
query = "SELECT * FROM dataset_restoran"
data = pd.read_sql(query, con=mydb)

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
daerah = 'Denpasar' 
tempat = 'Rumah Makan' 
kategori = 'Babi' 
jenis = 'Babi Guling' 
rasa = 'Gurih' 
harga = '30K' 
rating = 'Baik'

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

# Split Old Case and New Case
oldCase = mergeData.iloc[:-1]
newCase = mergeData.iloc[-1:]

# Indexing dengan K-Means

# Scaling Old Data
scaler = StandardScaler()
scaler.fit(oldCase)
old_scaled = scaler.transform(oldCase)
old_scaled = pd.DataFrame(old_scaled)

# Scaling All Data
scaler = StandardScaler()
scaler.fit(mergeData)
all_scaled = scaler.transform(mergeData)
all_scaled = pd.DataFrame(all_scaled)

# mengambil value scale kasus baru
coordInit = all_scaled.iloc[-1:]

# Clustering Data
kmeans = KMeans(n_clusters=3)
y_predicted = kmeans.fit_predict(old_scaled) 
oldCase['Cluster'] = y_predicted

# Euclidean Distance Between New Case And Centroid

# centroid cluster
listCentroid = kmeans.cluster_centers_

distance = list()
for i in range(len(listCentroid)):
    coordFinal = listCentroid[i]

    #distance from old with centroid
    dist = math.sqrt(((coordInit[0] - coordFinal[0]) ** 2) 
                    + ((coordInit[1] - coordFinal[1]) ** 2) 
                    + ((coordInit[2] - coordFinal[2]) ** 2)
                    + ((coordInit[3] - coordFinal[3]) ** 2)
                    + ((coordInit[4] - coordFinal[4]) ** 2)
                    + ((coordInit[5] - coordFinal[5]) ** 2)
                    + ((coordInit[6] - coordFinal[6]) ** 2))
    distance.append(dist)

# Mendapatkan Posisi Cluster Untuk Kasus Baru
minpos = distance.index(min(distance))
newCase['Cluster'] = minpos

# Create Cluster
#Merge Data
restaurant = [oldCase, newCase]
restaurant = pd.concat(restaurant).reset_index(drop=True)

# Tabel Cluster Kasus Baru
restaurant['Cluster']=restaurant['Cluster'].astype('int32')
newCluster = restaurant.loc[restaurant["Cluster"] == minpos]
total_rows = len(newCluster.index)

# Similarity dengan K-Nearest Neighbor
treshold_resto = knn_func(newCluster)

# Hasil Rekomendasi
solusi = treshold_resto.Index
solusi = np.array(solusi)
data_list = []
len_solution = len(treshold_resto)

if len_solution == 0:
    #Jika tidak ada rekomendasi masuk ke revise
    print("Mohon maaf, tidak ada rekomendasi untuk restoran yang anda cari \n Mohon menunggu pakar dalam mencari rekomendasi yang sesuai untuk anda")
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