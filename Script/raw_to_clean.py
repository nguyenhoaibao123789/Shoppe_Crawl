import pandas as pd
import glob

def read_all_csv(path):
    """
    Read all CSV files in the specified path

        Parameter:
            path(string): Path to folder contain CSV files
        Return:
            df(dataframe): A dataframe made of several CSV files
    """
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
    """
    Print the Dataframe basic information
    """
    print("----------------------Dataframe info---------------------------------")
    print(df.info())
    print("\nNumber of null value per column:\n",df.isnull().sum())
    print("\nNumber of product crawled per minute:\n ",df.groupby(df['crawl_timestamp'])['product_name'].count())
    print("\nAverage number of product crawled per minute: ",round(df.groupby(df['crawl_timestamp'])['product_name'].count().mean(),2))

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
    """
    Handle product sold number, if sold number contain "tr" then remove it and multiply by a milion
        Parameter:
            row(str): Dataframe row
        Return
            row(str): Dataframe row
    """
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
