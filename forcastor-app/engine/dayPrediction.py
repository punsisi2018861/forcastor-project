import requests
from bs4 import BeautifulSoup as bs
import sys
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
import time
from sklearn.preprocessing import MinMaxScaler
import keras
import os
import warnings
warnings.filterwarnings("ignore")

filePath = sys.argv[1]


def order_cluster(df, target_field_name, cluster_field_name, ascending):
    # Add the string "new_" to cluster_field_name
    new_cluster_field_name = "new_" + cluster_field_name
    
    # Create a new dataframe by grouping the input dataframe by cluster_field_name and extract target_field_name 
    # and find the mean
    df_new = df.groupby(cluster_field_name)[target_field_name].mean().reset_index()
    
    # Sort the new dataframe df_new, by target_field_name in descending order
    df_new = df_new.sort_values(by=target_field_name, ascending=ascending).reset_index(drop=True)
    
    # Create a new column in df_new with column name index and assign it values to df_new.index
    df_new["index"] = df_new.index
    
    # Create a new dataframe by merging input dataframe df and part of the columns of df_new based on 
    # cluster_field_name
    df_final = pd.merge(df, df_new[[cluster_field_name, "index"]], on=cluster_field_name)
    
    # Update the dataframe df_final by deleting the column cluster_field_name
    df_final = df_final.drop([cluster_field_name], axis=1)
    
    # Rename the column index to cluster_field_name
    df_final = df_final.rename(columns={"index": cluster_field_name})
    
    return df_final

def get_predictions(file_path):
    # Loading the data
    df = pd.read_excel(file_path)
    df.rename(columns={'Invoice':'InvoiceNo', 'Customer ID':'CustomerID', 'Price':'UnitPrice'}, inplace=True)

    df_data = df.dropna()
    df_data.InvoiceDate = pd.to_datetime(df_data.InvoiceDate)
    df_data['InvoiceYearMonth'] = df_data['InvoiceDate'].map(lambda date: 100*date.year + date.month)
    df_data['Revenue'] = df_data.UnitPrice * df_data.Quantity
    ctm_revenue = df_data.groupby('InvoiceYearMonth').Revenue.sum().reset_index()

    ctm_bhvr_dt = df_data[(df_data.InvoiceDate < pd.Timestamp(2011,9,1)) & 
        (df_data.InvoiceDate >= pd.Timestamp(2009,12,1))].reset_index(drop=True)


    ctm_next_quarter = df_data[(df_data.InvoiceDate < pd.Timestamp(2011,12,1)) & 
        (df_data.InvoiceDate >= pd.Timestamp(2011,9,1))].reset_index(drop=True)

    # Get the distinct customers in the dataframe ctm_bhvr_dt
    ctm_dt = pd.DataFrame(ctm_bhvr_dt['CustomerID'].unique())

    # Rename the column to CustomerID.
    ctm_dt.columns = ['CustomerID']

    # Create a dataframe with CustomerID and customers first purchase 
    # date in ctm_next_quarter
    ctm_1st_purchase_in_next_quarter = ctm_next_quarter.groupby('CustomerID').InvoiceDate.min().reset_index()
    ctm_1st_purchase_in_next_quarter.columns = ['CustomerID','MinPurchaseDate']

    ctm_last_purchase_bhvr_dt = ctm_bhvr_dt.groupby('CustomerID').InvoiceDate.max().reset_index()
    ctm_last_purchase_bhvr_dt.columns = ['CustomerID','MaxPurchaseDate']

    # Merge two dataframes ctm_last_purchase_bhvr_dt and ctm_1st_purchase_in_next_quarter
    ctm_purchase_dates = pd.merge(ctm_last_purchase_bhvr_dt, ctm_1st_purchase_in_next_quarter, on='CustomerID', 
                                how='left')

    ctm_purchase_dates['NextPurchaseDay'] = (ctm_purchase_dates['MinPurchaseDate'] - ctm_purchase_dates['MaxPurchaseDate']).dt.days

    # merge with ctm_dt 
    ctm_dt = pd.merge(ctm_dt, ctm_purchase_dates[['CustomerID','NextPurchaseDay']], on='CustomerID', how='left')

    ctm_dt = ctm_dt.fillna(9999)

    ctm_max_purchase = ctm_bhvr_dt.groupby('CustomerID').InvoiceDate.max().reset_index()
    ctm_max_purchase.columns = ['CustomerID','MaxPurchaseDate']

    # Find the recency in days 
    ctm_max_purchase['Recency'] = (ctm_max_purchase['MaxPurchaseDate'].max() - ctm_max_purchase['MaxPurchaseDate']).dt.days

    # Merge the dataframes ctm_dt and ctm_max_purchase[['CustomerID', 'Recency']] on the CustomerID column.
    ctm_dt = pd.merge(ctm_dt, ctm_max_purchase[['CustomerID', 'Recency']], on='CustomerID')

    number_of_clusters = 4

    kmeans = KMeans(n_clusters=number_of_clusters)
    kmeans.fit(ctm_dt[['Recency']])
    ctm_dt['RecencyCluster'] = kmeans.predict(ctm_dt[['Recency']])
    ctm_dt = order_cluster(ctm_dt, 'Recency', 'RecencyCluster', False)

    #get order counts for each user and create a dataframe with it
    ctm_frequency = df_data.groupby('CustomerID').InvoiceDate.count().reset_index()
    ctm_frequency.columns = ['CustomerID','Frequency']

    #add this data to our main ctm_dt
    ctm_dt = pd.merge(ctm_dt, ctm_frequency, on='CustomerID')

    kmeans = KMeans(n_clusters=number_of_clusters)
    kmeans.fit(ctm_dt[['Frequency']])
    ctm_dt['FrequencyCluster'] = kmeans.predict(ctm_dt[['Frequency']])

    ctm_dt = order_cluster(ctm_dt, 'Frequency', 'FrequencyCluster', False)

    ctm_revenue = df_data.groupby('CustomerID').Revenue.sum().reset_index()

    #merge it with our ctm_dt
    ctm_dt = pd.merge(ctm_dt, ctm_revenue, on='CustomerID')

    #apply clustering
    kmeans = KMeans(n_clusters=number_of_clusters)
    kmeans.fit(ctm_dt[['Revenue']])
    ctm_dt['RevenueCluster'] = kmeans.predict(ctm_dt[['Revenue']])

    #order the cluster numbers
    ctm_dt = order_cluster(ctm_dt, 'Revenue', 'RevenueCluster', True)

    #calculate overall score and use mean() to see details
    ctm_dt['OverallScore'] = ctm_dt['RecencyCluster'] + ctm_dt['FrequencyCluster'] + ctm_dt['RevenueCluster']
    ctm_dt['Segment'] = 'Low-Value'
    ctm_dt.loc[ctm_dt['OverallScore'] > 4, 'Segment'] = 'Mid-Value'
    ctm_dt.loc[ctm_dt['OverallScore'] > 6, 'Segment'] = 'High-Value'

    #create ctm_class as a copy of ctm_dt before applying get_dummies
    ctm_class = ctm_dt.copy()
    ctm_class = pd.get_dummies(ctm_class)
    ctm_class.head()

    ctm_class['NextPurchaseDayRange'] = 2  ## first week
    ctm_class.loc[ctm_class.NextPurchaseDay>30,'NextPurchaseDayRange'] = 1 # 4th week
    ctm_class.loc[ctm_class.NextPurchaseDay>90,'NextPurchaseDayRange'] = 0 # more than 3 months
    ctm_class['NextPurchaseDayRange'] = ctm_class['NextPurchaseDayRange'].map({0: "month_1", 1: "month_3", 2: "next_quarter"})

    user_df = ctm_class.copy()
    ctm_class = ctm_class.drop('NextPurchaseDay', axis=1)
    ctm_class = ctm_class.drop('CustomerID', axis=1)
    ctm_class = ctm_class.drop('NextPurchaseDayRange', axis=1)
    # y = to_categorical(y)

    sc = MinMaxScaler(feature_range=(0, 1))
    X = sc.fit_transform(ctm_class)

    model = keras.models.load_model ("engine/model/txnDayPredictionModel.h5") 
    pred= model.predict(X)

    # Create a new dataframe with the user ID column from tx_class
    predictions_df = user_df[['CustomerID']].copy()

    # Add the transaction day with the highest probability as a column to the predictions_df
    predictions_df['predicted_transaction_day'] = np.argmax(pred, axis=1)

    # Merge the predictions_df with the tx_class dataframe based on the user ID column
    merged_df = pd.merge(user_df, predictions_df, on='CustomerID')
    merged_df = merged_df.drop('predicted_transaction_day', axis=1)
    merged_df = merged_df.drop('Segment_Mid-Value', axis=1)
    merged_df = merged_df.drop('Segment_Low-Value', axis=1)
    merged_df = merged_df.drop('Segment_High-Value', axis=1)
    merged_df = merged_df.drop('Revenue', axis=1)
    merged_df = merged_df.drop('NextPurchaseDay', axis=1)
    merged_df = merged_df.drop('Recency', axis=1)
    merged_df = merged_df.drop('Frequency', axis=1)

    html_data_table = merged_df.to_html()

    if os.path.exists("gui/datatable1.html"):
        os.remove("gui/datatable1.html")
    
    text_file = open("gui/datatable1.html", "w")
    text_file.write(html_data_table)
    text_file.close()
    output = "Prediction Completeddd!"

    return output

print(get_predictions(filePath))
sys.stdout.flush()
