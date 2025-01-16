
import json
from typing import List
from urllib import parse, request

def ddg_query(search_term: str, nr_results: int) -> List[str]:
 
    #encode the search term for use in a URL
    encoded_query = parse.quote(search_term)
    url = f"https://api.duckduckgo.com/?q={encoded_query}&format=json" 
  
    try:
        #HTTP request
        with request.urlopen(url) as response: 
            body = response.read().decode('utf-8')   
 
        # parse the json response
        data = json.loads(body)
  
        # extracr the main topics URL if available
        main_url = data.get("AbstractURL", None)
  
        # extracr URLs from the related topics
        results = data.get("RelatedTopics", [])
        related_urls = [item.get("FirstURL") for item in results if "FirstURL" in item]
    
        #combine and prioritize the main URL
        urls = [main_url] if main_url else []
        urls.extend(related_urls)
  
        #return the top nr_results URLs, or all if fewer are found
        return urls[:nr_results]
     
    except Exception as e:
        print(f"error  : {e}") 
        return []
   
def last_modified(url: str) -> str:
      
    try:  
        with request.urlopen(url) as response:
            last_modified_header = response.headers.get("Last-Modified")
            return last_modified_header
    except Exception as e:  
        print(f"An error occurred: {e}")
        return None  
                               
search_query = "University of Peradeniya"  
results_count = 1   
urls = ddg_query(search_query, results_count)  
print("Extracted URLs:") 
for url in urls: 
    print(url) 
 
#check Last-Modified header
if urls:
    print("\nLast-Modified header for the first URL:") 
    print(last_modified(urls[0]))

 
