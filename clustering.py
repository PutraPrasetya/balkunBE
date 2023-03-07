import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import math

def cluster_kmeans(mergeData):
    # Split Old Case and New Case
    oldCase = mergeData.iloc[:-1]
    newCase = mergeData.iloc[-1:]
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
    # Merge Data
    restaurant = [oldCase, newCase]
    restaurant = pd.concat(restaurant).reset_index(drop=True)
    # Tabel Cluster Kasus Baru
    restaurant['Cluster']=restaurant['Cluster'].astype('int32')
    newCluster = restaurant.loc[restaurant["Cluster"] == minpos]
    
    return newCluster