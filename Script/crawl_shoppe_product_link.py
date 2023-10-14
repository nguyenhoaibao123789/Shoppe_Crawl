from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from seleniumbase import Driver
import pandas as pd
from time import sleep
from zoneinfo import ZoneInfo

def init_driver(url):
    """
    Create the driver to crawl data from website

        Parameter:
            url(string): URL of the website need to be crawled

        Return:
            driver(selenium object): Driver for crawling purpose
    """
    driver = Driver(uc=True,incognito=True,chromium_arg='disable-blink-features="AutomationControlled"')
    driver.maximize_window()
    try:
        driver.get(url)
        print("Driver initiated successfully")
        sleep(6)
    except:
        print("URL not valid")
    return driver

def scroll_to_category_section(driver):
    """
    Close advertise that pop up when access home page (if any) and scroll to the category section

        Parameter:
            driver(selenium object): Driver for crawling purpose
    """
    try:
        #close home advertise
        close_btn = driver.execute_script('return document.querySelector("#main shopee-banner-popup-stateful").shadowRoot.querySelector("div.home-popup__close-area div.shopee-popup__close-btn")')
        close_btn.click()
        print("Closed home ad ")
    except:
        print("No ad to close")
    
    try:
        #scroll into category section
        category_section=driver.find_element(By.XPATH,'//div[@class="home-category-list"]')
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", category_section)
        sleep(3)
    except:
        print("Cant find category section/Web page is closed")

def get_category(driver):
    """
    Crawl all categories available on shoppe home page and add them to a list

        Parameter:
            driver(selenium object): Driver for crawling purpose
        Return:
            df_category(dataframe): Dataframe contain the category name and their URL
    """
    category_list=[]
    #Find the view more button
    view_more_category_button=driver.find_element(By.XPATH, '//div[@class="carousel-arrow carousel-arrow--next carousel-arrow--hint"]')
    #If there are more categories to be viewed
    while view_more_category_button.get_attribute('style').find("visible") != -1:
        #Find the list of all categories
        data=driver.find_elements(By.XPATH,'//a[@class="home-category-list__category-grid"]')
        for value in data:
            print("category: {}, href:{}".format(value.text,value.get_attribute('href')))
            #If category name is not Null then add its name and URL to the list
            if value.text != '':
                category_list.append([value.text,value.get_attribute('href')])
        try:
            #Click the view more button once done getting all the viewable categories and update status of the view more button
            view_more_category_button.click()
            view_more_category_button=driver.find_element(By.XPATH, '//div[@class="carousel-arrow carousel-arrow--next carousel-arrow--hint"]')
        except:
            continue
    df_category=pd.DataFrame(category_list,columns=["Category_name","Category_URL"])
    print("All categories available on Shoppe:\n",df_category)
    return df_category

def get_subcategory(driver,df_category):
    """
    For each category, crawl all their subcategories and add them to a list

        Parameter:
            driver(selenium object): Driver for crawling purpose
            df_category(dataFrame): A DataFrame contain all categories name and their URL
        Return:
            df_subcategory(dataFrame): A DataFrame of all subcategories, contains the category name of the subcategory, subcategory name, subcategory URL
    """
    sub_category_list=[]
    for url in df_category["Category_URL"]:
        driver.get(url)
        sleep(3)
        category_name_var=df_category['Category_name'].loc[df_category['Category_URL']==url].item()
        print("category name: ", category_name_var)
        try:
            see_more_btn=driver.find_element(By.XPATH, '//div[@class="shopee-category-list__toggle-btn"]')
            see_more_btn.click()
            sleep(3)
        except:
            print("no button found")
        try:
            sub_cat_section= driver.find_element(By.XPATH, '//div[@class="shopee-category-list__category"]')
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", sub_cat_section)
        except:
            print("cant scroll down to specific section")
        sub_cats=driver.find_elements(By.XPATH, '//a[@class="shopee-category-list__sub-category"]')
        for sub_category in sub_cats:
            print("subcategory name: ",sub_category.text)
            sub_category_list.append([category_name_var,sub_category.text,sub_category.get_attribute('href')])
    df_subcategory=pd.DataFrame(sub_category_list,columns=["Category_name","Subcategory_name","Subcategory_URL"])
    print("All subcategory available on Shoppe:\n",df_subcategory)
    return df_subcategory

def get_page_link_for_each_subcategory(driver,df_subcategory):
    """
    Every subcategory has many pages of product, this function aim to get all the links to these pages

        Parameter:
            driver(selenium object): Driver for crawling purpose
            df_subcategory(DataFrame): DataFrame contains subcategory data
        Return:
            df_subcategory(DataFrame): The input Dataframe with new page links for each subcategory are appended
    """
    count=0
    number_of_subcategory=len(df_subcategory)
    for url in df_subcategory["Subcategory_URL"]:
        count=count+1
        print("subcategory number: {}/{}".format(count,number_of_subcategory))
        try:
            driver.get(url)
            sleep(3)
        except:
            print("unable to get url")
            continue
        try:
            sub_category_name=df_subcategory["Subcategory_name"].loc[df_subcategory["Subcategory_URL"]==url].item()
        except:
            print("unable to get subcategory name")
            sub_category_name=''
            pass
        try:
            category_name=df_subcategory["Category_name"].loc[df_subcategory["Subcategory_URL"]==url].item()
        except:
            print("unable to get category name")
            category_name=''
            pass
        try:
            total_page=int(driver.find_element(By.CLASS_NAME,"shopee-mini-page-controller__total").text)
            print("subcategory name: {}, total page: {}".format(sub_category_name,total_page))
        except:
            print("cant find total page")
            continue
        try:
            if total_page > 1:
                for i in range(1,total_page):
                    df_subcategory.loc[len(df_subcategory)]=(category_name,sub_category_name,url+"?page="+str(i))
                    print(url+"?page="+str(i))
        except:
            print("cant generate new link")
            continue
    try:
        df_subcategory.sort_values(["Category_name","Subcategory_name"], ascending= True,inplace=True,ignore_index=True)
    except:
        print("cant sort df")
    print("All subcategory and their pages URL on Shoppe:\n",df_subcategory)
    return df_subcategory

def get_all_product_link(driver,df_subcategory_with_all_page):
    """
    For each page link, get all the product links available on that page

        Parameter:
            driver(selenium object): Driver for crawling purpose
            df_subcategory_with_all_page(DataFrame):DataFrame converted from the new subcategory list that 
                                                    contain all page links for eahc subcategory
        Return:
            df_product_link(DataFrame): DataFrame contain all product links as well as the product category and subcategory
    """
    product_link_list=[]
    count=0
    for url in df_subcategory_with_all_page["Subcategory_URL"]:
        print("url number: {}/{}".format(count,len(df_subcategory_with_all_page)))
        print(url)
        try:
            driver.get(url)
            sleep(3)
        except:
            print("url corrupted")
            count=count+1
            continue
        try:
            sub_category_name=df_subcategory_with_all_page["Subcategory_name"].loc[df_subcategory_with_all_page["Subcategory_URL"]==url].item()
        except:
            print("unable to get subcategory name")
            sub_category_name=''
            pass
        try:
            category_name=df_subcategory_with_all_page["Category_name"].loc[df_subcategory_with_all_page["Subcategory_URL"]==url].item()
        except:
            print("unable to get category name")
            category_name=''
            pass
        try:
            product_section=driver.find_element(By.XPATH, '//div[@class="QWD0QP"]')
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'center'});", product_section) #scroll down to the bottom of the page
            sleep(3)
        except:
            print("cant find product section")
            count=count+1
            continue
        try:
            product_list=driver.find_elements(By.XPATH, '//a[@data-sqe="link"]')
            print("number of product on this page: ",len(product_list))
        except:
            print("cant get product link list")
            count=count+1
            continue
        product_link_count=0
        for product in product_list:
            try:
                product_link=product.get_attribute('href')
                product_link_list.append([category_name,sub_category_name,product_link])
                product_link_count=product_link_count+1
            except:
                print("cant get product link")
                continue
        print("product link added: {}/{}".format(product_link_count,len(product_list)))
        count=count+1
    df_product_link=pd.DataFrame(product_link_list,columns=["Category_name","Subcategory_name","Product_URL"])
    print("All product link on Shoppe:\n",df_product_link)
    return df_product_link

if __name__=='__main__':
    driver=init_driver('https://shopee.vn')
    scroll_to_category_section(driver)

    df_category=get_category(driver)
    df_category.drop_duplicates(inplace=True,ignore_index=True)
    df_category = df_category.loc[df_category["Category_name"] != '']
    
    df_subcategory=get_subcategory(driver,df_category)
    df_subcategory_all_page_link=get_page_link_for_each_subcategory(driver,df_subcategory)

    df_product_link=get_all_product_link(driver,df_subcategory_all_page_link)
    df_product_link.to_csv("Data/all_product_link.csv",index=False)
