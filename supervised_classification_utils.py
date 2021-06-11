#!/usr/bin/env python
# coding: utf-8

# In[1]:


def classifier(data,test):
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import RandomForestClassifier
    best_columns=['s_ORF1ab', 'del_ORF1ab', 'mnc_S', 'del_S', 's_E', 's_M', 'mc_N',
       'mnc_N', 'del_N', 'mnc_NON_COD']
    print('ciao')
    target = data['label']
    data=data[best_columns]
    test=test[best_columns]
    
    ss=StandardScaler()
    data=ss.fit_transform(data)
    test=ss.transform(test)
    clf =RandomForestClassifier(random_state=42,max_depth=10,n_estimators=10) 
    clf.fit(data,target)
    target_test = clf.predict(test)
    import seaborn as sns
    import matplotlib.pyplot as plt
    map = {0 : "Original", 1 : "Californian", 2 : "Brazilian", 3 : "English", 4 : "Nigerian", 5 : "South African"}
    pred=[]
    for line in prediction:
        pred.append(map[line])
    pred_df=pd.DataFrame()
    pred_df['Variant']=pred
    ax=sns.countplot(x='Variant',data=pred_df,palette='Paired')
    
    
    
    return target_test
    
