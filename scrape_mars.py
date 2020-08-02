import pandas as pd
from bs4 import BeautifulSoup as bs
from splinter import Browser
import time
import pymongo



def insert_data_in_db(data):
    # Create connection variable
    conn = 'mongodb://localhost:27017'

    # Pass connection to the pymongo instance.
    client = pymongo.MongoClient(conn)

    #Select database to use
    db=client.mars_db

    # Drops collection if available to remove duplicates
    db.mars_data.drop()

    #Insert data from mars_data in the database
    #for i in range(len(data)):
        #db.mars_data.update_one(data[i],data[i],upsert=True)

    #db.mars_data.update({}, data, upsert=True)
    db.mars_data.insert_many(data)

def init_browser():

    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)


def scrape():

    browser = init_browser()
    mars_data = []
    
    ### Get latest Article on Monn from NASA website
    
    
    #Set Mars NASA website URL
    mars_nasa_url = 'https://mars.nasa.gov/news'
    #Vist the URL
    browser.visit(mars_nasa_url)
    #Adding time.sleep(5) to allow the webpage to load completely before taking the html of the page
    time.sleep(5)
    mars_nasa_html = browser.html
    #Using BeautifulSoup to scrape the website to find the latest article
    soup_mars_news = bs(mars_nasa_html, 'lxml')

    #Finding article and assigning title and description of article to news_title and news_p variables respectively
    article = soup_mars_news.find("div", class_='list_text')
    #print(article)
    news_title=article.find('div',class_="content_title").text 
    news_p=article.find('div',class_="article_teaser_body").text

    # Adding the news title in the mars_data dictionary
    mars_data.append({"NewsTitle":news_title})
    #Adding brief description in the mars_data dictionary
    mars_data.append({"NewsDescription":news_p})

    

    ###Finding JPL Mars Space Featured Image URL

    #Set Space image website URL
    space_image_url="https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
    #Visit the website
    browser.visit(space_image_url)  
    #Adding time.sleep(5) to allow the webpage to load completely before taking the html of the page
    time.sleep(2)
    space_image_browse=browser.html

    #Creating soup object for web scrapping
    soup_space_image=bs(space_image_browse,'lxml')
    #Finding the URL of the image and adding website URL to get the full URL
    featured_image_url="https://www.jpl.nasa.gov"+soup_space_image.find('article',class_="carousel_item")['style'].replace("background-image: url('",'').replace("""');""","")

    # Adding the image path in the mars_data dictionary
    mars_data.append({"FeaturedImage":featured_image_url})


    ###Get Mars Fact Data Table

    #Set Mars fact website URL
    mars_fact_url="https://space-facts.com/mars/"

    #Read all the table from the html
    page_tables=pd.read_html(mars_fact_url)

    #Adding 2 secs delay
    time.sleep(2)
    
    #Assigning the first table which has mars data to a dataframe
    mars_fact_df=page_tables[0]
    #Renaming columns to meaning ful name
    mars_fact_df.columns=["Description","Mars"]

    #Setting mars Fact as index of dataframe
    mars_fact_df.set_index("Description",inplace=True)

    # Create html table from dataframe
    mars_fact_table=mars_fact_df.to_html()

    #Remove "/n" values in the html
    mars_fact_table.replace('\n', '')

    #Add html table to mars data dictionary
    mars_data.append({"MarsFact":mars_fact_table})

    ###Get Northern Hemisphere images

    #Creating list to hold name and URL for each hemisphere full image
    hemisphere_image_urls=[]
    #Set URL of Mars' hemisphere main page
    mars_hemisphere_image_url="https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
    #Visit the website
    browser.visit(mars_hemisphere_image_url)

    #Adding time.sleep(2) to allow the webpage to load completely before taking the html of the page
    time.sleep(2)
    mars_hemisphere_html=browser.html

    #Creating Beautiful soup object for the html
    soup_mars_hemisphere=bs(mars_hemisphere_html,'lxml')

    # Finding the URL where the full image for each hemisphere would be available
    images_list=soup_mars_hemisphere.find("div",class_="collapsible results")
    #Creating dictionary to store hemisphere name and URL where the full image for each hemisphere is available
    full_image_url_dict={}
    #Iterate and store name and URL for each hemisphere full image 
    for i in range(4):
        full_image_url="https://astrogeology.usgs.gov/"+images_list.find_all("div",class_="item")[i].find('a')["href"]
        full_image_name=images_list.find_all("div",class_="item")[i]\
        .find('div',class_="description")\
        .find('h3').text
        full_image_url_dict[full_image_name]=full_image_url

    #Iterate over dictionary created above and visit each page and find the URL of image 
    # and add it to using Hemisphere name from full_image_url_dict

    for key, value in full_image_url_dict.items():
        browser.visit(value)
        full_image_html=browser.html
        full_image_soup=bs(full_image_html,'lxml')
        img_url=full_image_soup.find("div",class_="downloads").find("a")["href"]
        hemisphere_image_urls.append({"title":key, "img_url": img_url})

    #Adding Mars Hemispheres image data to mars data dictionary
    mars_data.append({"HemisphereImage":hemisphere_image_urls})

    # Close the browser after scraping
    browser.quit()

    #print(mars_data)

    #for i in range(len(mars_data)):
        #print(mars_data[i])
    
    insert_data_in_db(mars_data)
 

#scrape()

