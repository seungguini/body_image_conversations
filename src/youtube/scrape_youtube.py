# import required libraries
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-dev-shm-usage')
import time
import csv

# function to scrape videos titles absed on a youtube search url
# @returns 
def scrape_videos(query):
    """
    Scrape top YouTube videos based on search query and return a list of dictionaries containing video data
    
    
    """
    
    # scrape search results
    link = "https://www.youtube.com/results?search_query=" + query
            
    # open chrome driver - headless
    driver = webdriver.Chrome(executable_path='C:/WebDriver/bin/chromedriver.exe',chrome_options=chrome_options)
    driver.get(link)
    
    print("=" * 40)  # Shows in terminal when youtube summary page with search keyword is being scraped
    print("Scraping " + link)    
    
    time.sleep(5)
    
    # scroll 10 times
    for i in range(0,5):
        driver.execute_script("window.scrollTo(0,Math.max(document.documentElement.scrollHeight,document.body.scrollHeight,document.documentElement.clientHeight))")
        print("scrolling to load more comments")
        time.sleep(4)
    # scrape top 8 video URLS that pop up on search
    video_list = driver.find_elements_by_xpath('//*[@id="video-title"]')
    
    videos = []
    
    # store URL and video title for videos
    for video in video_list:
        v = {
            'url' : video.get_attribut('href'),
            'title' : video.get_attribute('title'),
            'query' : query
        }
        videos.append(v)
    
    return videos    
    
def scrape_youtube(videos):
    path = "../../data/youtube_comments.csv"
    csv_file = open(path,'w', encoding="UTF-8", newline="")
    writer = csv.writer(csv_file)    
    # Write header names
    writer.writerow(['url', 'link_title', 'channel', 'no_of_views', 'time_uploaded', 'comment', 'author', 'comment_posted', 'no_of_replies','upvotes','downvotes'])
    
    
    # Scrape search results - headless
    driver = webdriver.Chrome(executable_path='C:/WebDriver/bin/chromedriver.exe')

    for video in videos:
        url = video['url']
        title = video['title']
        query = video['query']
        
        print("=" * 40)
        print("video title : ", title)
        
        driver.get(url)
        
        # Scraping video info
        v_channel = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#upload-info yt-formatted-string"))).text
        print("channel : ",v_channel)    
        v_views = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#count span.view-count"))).text
        print("no. of views : ",v_views)
        v_timeUploaded = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#date yt-formatted-string"))).text
        print("time uploaded : ",v_timeUploaded)
        w = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#top-level-buttons yt-formatted-string")))
        w = driver.find_elements_by_css_selector("div#top-level-buttons yt-formatted-string")
        v_likes = w[0].text
        v_dislikes = w[1].text
        print("video has ", v_likes, "likes and ", v_dislikes, " dislikes")
        
        youtube_dict ={}    
    
        print("Scraping child links ")

        # Wait for comments to load
        driver.execute_script('window.scrollTo(0,390);')
        time.sleep(2)
    
        try:  # Check if comments are enabled for video

            # Sort by Top Comments        
            sort = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR,"div#icon-label")))
            sort.click()
                
            topcomments = driver.find_element_by_xpath("""//*[@id="menu"]/a[1]/paper-item/paper-item-body/div[1]""")
            topcomments.click()
            
    
            # Loads 20 comments , scroll five times to load next set of 40 comments. 
            for i in range(0,5):
                driver.execute_script("window.scrollTo(0,Math.max(document.documentElement.scrollHeight,document.body.scrollHeight,document.documentElement.clientHeight))")
                print("scrolling to load more comments")
                time.sleep(4)
    
            # Count total number of comments and set index to number of comments if less than 50 otherwise set as 50. 
            totalcomments= len(driver.find_elements_by_xpath("""//*[@id="content-text"]"""))
            
    
            if totalcomments < 100:
                index= totalcomments
            else:
                index= 100 
            
            # Loop through each comment and scrape data
            print("scraping through comments")
            ccount = 0
            while ccount < index: 
                try:
                    comment = driver.find_elements_by_xpath('//*[@id="content-text"]')[ccount].text
                except:
                    comment = ""
                try:
                    authors = driver.find_elements_by_xpath('//a[@id="author-text"]/span')[ccount].text
                except:
                    authors = ""
                try:
                    comment_posted = driver.find_elements_by_xpath('//*[@id="published-time-text"]/a')[ccount].text
                except:
                    comment_posted = ""
                try:
                    replies = driver.find_elements_by_xpath('//*[@id="more-text"]')[ccount].text                    
                    if replies =="View reply":
                        replies= 1
                    else:
                        replies =replies.replace("View ","")
                        replies =replies.replace(" replies","")
                except:
                    replies = ""
                try:
                    upvotes = str(driver.find_elements_by_xpath('//*[@id="vote-count-middle"]')[ccount].text)
                except:
                    upvotes = ""
                
                # Build dictionary and write to CSV
                youtube_dict['query'] = query
                youtube_dict['url'] = url
                youtube_dict['title'] = title
                youtube_dict['likes'] = v_likes
                youtube_dict['dislikes'] = v_dislikes
                youtube_dict['channel'] = v_channel
                youtube_dict['no_of_views'] = v_views
                youtube_dict['time_uploaded'] = v_timeUploaded
                youtube_dict['comment'] = comment
                youtube_dict['author'] = authors
                youtube_dict['comment_posted'] = comment_posted
                youtube_dict['no_of_replies'] = replies
                youtube_dict['upvotes'] = upvotes
                writer.writerow(youtube_dict.values())
                
                # Increment comment counter
                ccount = ccount + 1
                
        # If video errors out, move onto the next one
        except TimeoutException as e:
            print(title, "  errored out: ",str(e))
            print("moving onto next video")