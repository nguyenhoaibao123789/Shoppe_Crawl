import pandas as pd
import glob
from numpy import nan
from datetime import datetime
import re

def read_all_csv(path):
    all_files=glob.glob(path)
    list_df=[]
    for file in all_files:
        print(file)
        df=pd.read_csv(file,encoding='utf_16')
        list_df.append(df)

    df = pd.concat(list_df, axis=0, ignore_index=True)
    df.drop_duplicates(inplace=True,subset="product_name")
    return df

def get_dataframe_info(df):
    print(df.info())
    print("number of null value per column: ",df.isnull().sum())
    print("number of product crawled per minute: ",df.groupby(df['crawl_timestamp'])['product_name'].count())
    print("average number of product crawled per minute: ",df.groupby(df['crawl_timestamp'])['product_name'].count().mean())

def handle_product_price(row):
    """
    Handle product price, if price is a range then take the minium number

        Parameter:
            row(str): Dataframe row
        Return
            row(str): Dataframe row
    """
    if "-" in row:
        row=int(row.split("-")[0].replace(".","").replace("₫",""))
    else:
        row=int(row.replace(".","").replace("₫",""))
    return row

def handle_product_sold(row):
    try:
        if "tr" in row:
            row=int(float(row.replace("tr","").replace(",","."))*1000000)
    except:
        row=int(row)
    return row

if __name__=='__main__':
    df=read_all_csv("Data/Raw_product_data/*.csv")
    get_dataframe_info(df)
    df['product_price']=df['product_price'].map(lambda row:handle_product_price(row))
    df['product_sold']=df['product_sold'].map(lambda row: handle_product_sold(row)).astype('int')
    df['product_revenue']=df['product_price']*df['product_sold']
    df_final=df[["product_name","product_url","product_rating","product_price","product_revenue"]]
    df_final.to_csv("Data/Clean_product_data/product.csv",index=False)
