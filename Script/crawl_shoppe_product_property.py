from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from seleniumbase import Driver
import pandas as pd
from time import sleep
import time
import random
import argparse

def terminal_input():
    parser = argparse.ArgumentParser()
    # Adding optional argument
    parser.add_argument("-s", "--StartIndex",type=int)
    parser.add_argument("-r", "--Reduce",type=str,default="true")
    args = parser.parse_args()
    start_index=args.StartIndex
    is_reduce=args.Reduce.lower()
    return start_index,is_reduce

def init_driver():
    """
    Create the driver to crawl data from website using undetected chrome and an extension that change header of request send to website

        Return:
            driver(selenium object): Driver for crawling purpose
    """
    driver = Driver(uc=True,incognito=True,chromium_arg='disable-blink-features="AutomationControlled"',extension_dir="extension",undetected=True,undetectable=True,use_auto_ext=False)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    driver.maximize_window()
    return driver

def crawl_shoppe_product(driver,start_index,product_link_list):
    """
    Crawl the product property like name, price, sold number, rating and timestamp when they are crawled

        Parameter:
            driver(selenium object): Driver for crawling purpose
            start_index(int): Index of URL in dataframe at which crawler should start
            product_link_list(list): List of product URLs
    """
    count=start_index
    product_property=[]
    detected_count=0
    for product_link in product_link_list[start_index:]:
        print("number of product: {}/{}".format(count,len(product_link_list)))
        try:
            driver.get(product_link)
            sleep(random.randint(4, 9))
        except:
            pass
        #Get current timestamp when the product property is crawled
        crawl_timestamp = time.strftime("%Y-%m-%d %H:%M", time.localtime())
        try:
            #If product name contain "Yêu Thích+" or "Yêu Thích", remove them
            product_name=driver.find_element(By.XPATH, '//div[@class="_44qnta"]').text
            if "Yêu Thích\n" in product_name or "Yêu Thích+\n" in product_name:
                product_name=product_name.replace("Yêu Thích\n","").replace("Yêu Thích+\n","")
        except:
            print('failed to retrieve product name')
            print(product_link)
            product_name=''
        try:
            try:
                product_price=driver.find_element(By.XPATH, '//div[@class="Y3DvsN"]').text
            except NoSuchElementException:
                product_price=driver.find_element(By.XPATH, '//div[@class="pqTWkA"]').text
        except:
            print('failed to retrieve product price')
            print(product_link)
            product_price=''
        try:
            product_rating=float(driver.find_element(By.XPATH, '//div[@class="_1k47d8 _046PXf"]').text)
        except:
            print('failed to retrieve product rating')
            print(product_link)
            product_rating=''
        try:
            product_sold=driver.find_element(By.XPATH, '//div[@class="e9sAa2"]').text
            if "k" in product_sold:
                product_sold=int(float(product_sold.replace("k","").replace(",","."))) *1000
        except:
            print('failed to retrieve product sold')
            print(product_link)
            product_sold=''
        if product_name == '' and product_price == '' and product_rating =='' and product_sold=='':
            detected_count=detected_count+1
            print("Unable to extract information")
        else:
            product_property.append([product_name,product_link,product_rating,product_price,product_sold,crawl_timestamp])
        count=count+1
        random_choice=random.randint(0,1)
        if random_choice!=0:
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='UJO7PA']"))).click()
            except:
                print("cant click product image")
        if detected_count==3:
            print("Last product link processed successfully: ",count-3)
            print("Unable to extract information 3 times, proceed to stop crawling")
            print("Exporting data to csv")
            pd.DataFrame(product_property,columns=["product_name","product_url","product_rating","product_price","product_sold","crawl_timestamp"]).to_csv("Data/Raw_product_data/shoppe_product_final_{}_{}.csv".format(start_index,count-3),index=False,encoding="utf-16")
            print("Done")
            break
        sleep(random.randint(3, 7))
    pd.DataFrame(product_property,columns=["product_name","product_url","product_rating","product_price","product_sold","crawl_timestamp"]).to_csv("Data/Raw_product_data/shoppe_product_final_{}_{}.csv".format(start_index,count-3),index=False,encoding="utf-16")
    print("Complete crawling data from product links")
    return count-2

def reduce_df_by_category(df,category_column,number_of_row_per_category):
    """
    Take a certain number of rows for each product category

        Parameter:
            df(dataframe): Original dataframe that needs to be reduced
            category_column(string): Name of the column contains category name
            number_of_row_per_category(int): Number of rows to take per category
        Return:
            df_reduced(dataframe): New dataframe with specified number of rows per category
    """
    list_of_new_df=[]
    df_grouped=df.groupby(category_column)
    for column in df[category_column].unique():
        new_df=df_grouped.get_group(column)
        new_df=new_df[0:number_of_row_per_category]
        list_of_new_df.append(new_df)
    df_reduced=pd.concat(list_of_new_df)
    df_reduced.reset_index(inplace=True,drop=True)
    return df_reduced

if __name__=='__main__':
    start_index,is_reduce=terminal_input()
    df=pd.read_csv("Data/all_product_link.csv")
    if is_reduce=="true":
        print("Please specify number of product per category: ")
        reduce_size=int(input())
        df_final=reduce_df_by_category(df,"category_name",reduce_size)
    else:
        df_final=df

    if start_index>len(df_final):
        print("start index must be less than {}".format(len(df_final)))
    else:
        print("Number of product per category before reduce: ")
        print(df.groupby(["category_name"]).count())
        print("\nNumber of product per category after reduce: ")
        print(df_final.groupby(["category_name"]).count())
        while start_index<=len(df_final):
            driver=init_driver()
            start_index=crawl_shoppe_product(driver,start_index,list(df_final["product_link"])) #Use df instead of df_reduced if you do not wish to reduce the number of product
            if start_index>=len(df_final):
                break
            sleep(10)

