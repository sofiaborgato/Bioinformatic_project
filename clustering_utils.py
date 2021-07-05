#!/usr/bin/env python
# coding: utf-8

# In[1]:

#Function to compute the number of null values for each columns of the given dataset
def nullscan(df_check):
    df_nulls = (df_check == 0) 
    nulls_per_col = df_nulls.sum(axis=0)
    nulls_per_col /= len(df_check.index)
    for line,col_name in zip(nulls_per_col,df_check.columns):
        if line>0.99:#If the number of null values is >99% delete the columns
            df_check.drop(col_name,axis=1,inplace=True)
    return df_check


# In[ ]:


def clustering(control,test):
    import pandas as pd
    import numpy as np
    import seaborn as sns
    from sklearn.neighbors import NearestNeighbors
    from sklearn.cluster import DBSCAN
    from sklearn import metrics
    from statistics import mode
    import matplotlib.pyplot as plt
    #Concat the control dataset with the one given by the user(or in case the default ones)
    total=pd.concat([control,test])
    total=nullscan(total)#Check null values
    data=total.drop('label',axis=1,inplace=False)#Drop the true labels
    label=total['label']
    min_points=20#Set min points values for DBSCAN
    neighbors = NearestNeighbors(n_neighbors=2*len(total.columns),metric='euclidean')#Calculate the distances from the k nearest neighbors for each data 
    neighbors_fit = neighbors.fit(data)
    distances, indices = neighbors_fit.kneighbors(data)
    distances = np.sort(distances, axis=0)
    distances = distances[:,1]
    
    
    
    
    dist=pd.Series(distances)

    der1 = dist.diff()

    th=30
    counter = 0
    #Procedure to estimate the best eps number(well described in report)
    for i,k in enumerate(der1[:len(data)-1]):
        if k > -1:
            if k == 0:

                counter = counter + 1
            else:
                if counter < th:
                    best_eps=distances[i-1]
                    break
                else:
                    counter = 0
        
    print('best_eps= ' + str(best_eps))
    af = DBSCAN(eps=best_eps,min_samples=min_points,metric='euclidean').fit(data)#perform DBSCAN
    
    labels = af.labels_
    n_clusters_ = len(np.unique(labels))
    print('n_clusters:',n_clusters_)
    from sklearn import metrics
    print('Estimated number of clusters: %d' % n_clusters_)
    print("Homogeneity: %0.3f" % metrics.homogeneity_score(label, labels))
    print("Completeness: %0.3f" % metrics.completeness_score(label, labels))
    print("V-measure: %0.3f" % metrics.v_measure_score(label, labels))
    print("Adjusted Rand Index: %0.3f"
          % metrics.adjusted_rand_score(label, labels))
    print("Adjusted Mutual Information: %0.3f"
          % metrics.adjusted_mutual_info_score(label, labels))
    print("Silhouette Coefficient %0.3f"
          % metrics.silhouette_score(data, labels, metric='euclidean'))
    
    n_variants=len(pd.unique(control.label))
    n_clusters = len(pd.unique(labels))
    cl_dict={}
    
    possible_clusters=np.sort(pd.Series(labels).unique())
    cluster_out = []
    for l in possible_clusters:
        cl = label[labels==l]
        cluster_out.append(cl)
    
    for i in range(1,n_clusters): #for each cluster found with DBSCAN algo, assigne the label corresponding to the mode of the true label in the test set 
        if mode(cluster_out[i])==-1:#if the mode correspond to the unlabled data (-1) a new variant is found
            cl_dict[i-1]=n_variants #update the total num variants
            n_variants=n_variants+1
        else:
            cl_dict[i-1]=mode(cluster_out[i]) #else assigne the class mode to the cluster
    cl_dict[-1]=-1
    
    prediction = []
    for i in range(0,len(test)):
        prediction.append((cl_dict[labels[len(control)+i]]))  #Store the prediction in an array 
    prediction_pair=pd.DataFrame({'true_label':label,'pred':labels})


    # Create crosstab: ct
    ct = pd.crosstab(prediction_pair['true_label'], prediction_pair['pred'])

    # Display ct
    confusion_matrix=np.array(ct)

    m=[]
    #visualize result 
    map = {0 : "Original", 1 : "Californian", 2 : "Brazilian", 3 : "English", 4 : "Nigerian", 5 : "South African",-1:"Test samples"}
    for variant in range(-1,6):
      for cluster in range(-1,n_clusters-1):
        m.append([confusion_matrix[variant+1,cluster+1],map[variant],cluster])
    df=pd.DataFrame(m,columns=["Value", "Variant", "Cluster"])

    c = sns.color_palette('Paired')
    plot = sns.catplot(x="Cluster", y="Value", hue="Variant", kind="bar", data=df,height=7, aspect=1.4,palette="Paired")
    plt.ylabel('Number of samples', fontsize=13)
    plt.xlabel('Cluster', fontsize=13)
   
    fig = plot.fig
    fig.savefig('./Output/clustering_report_plot.png', bbox_inches='tight')
    
    return prediction, n_variants-len(pd.unique(control.label))

