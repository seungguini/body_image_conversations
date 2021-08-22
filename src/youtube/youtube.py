from scrape_youtube import scrape_videos, scrape_youtube
from process_youtube import process_data
from mongo_youtube import filter_urls, upload_data

# search terms for basic body image terms
search_terms_basic=["body+image","eating+disorder", "anorexia", "binge+eating"]

# search terms for negative /triggering body image content
search_terms_trigger = ["tw+ed", "losing+weight", "restricting", "thinspiration", "diet"]

for query in search_terms_basic:
    
    # scrape youtube titles based on query
    urls_titles = scrape_videos(query)
    
    # filter out duplicate videos based on DB
    urls_titles_filtered = filter_urls(urls_titles)
    
    # scrape comments based on filtered video list
    scrape_youtube(urls_titles_filtered, query)
    
    # Process youtube data into youtube_comments_clean.csv
    process_data()
    
    # upload data to DB
    upload_data()
    
    break