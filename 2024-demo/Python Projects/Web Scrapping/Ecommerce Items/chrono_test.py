import requests, re

def watch_url_1():

    headers = {
        'authority': 'www.chrono24.fr',
        'cache-control': 'max-age=0',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'referer': 'https://www.chrono24.fr/rolex/index.htm',
    #     'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }
    
    response = requests.get('https://www.chrono24.fr/rolex/index.htm', headers=headers)
    resp  = response.text
    
    test1_urls = []
    
    
    
    # open("sample.txt","w").write(resp)
    # print ("Completed")
    
    links_re = re.search(r'(?s)(<strong>Modèle</strong></div>.*?</ul></li></ul>)',str(resp))
    if links_re:
        links = links_re.group(1)
        
        urls_re = re.search(r'<a href="(.*?)"',str(links))
        if urls_re:
            for urls_link in re.finditer(r'<a href="(.*?)"',str(links)):
                urls = urls_link.group(1)
                urls = 'https://www.chrono24.fr'+str(urls)
                urls = re.sub(r"'",r"''",str(urls))
                brand = re.search(r'https://www\.chrono24\.fr/(.*?)/',urls).group(1)
                model = re.search(r'https://www\.chrono24\.fr/.*?/(.*?)--mod',urls).group(1)
                
#                 print ("urls:",urls)
                test1_urls.append(urls)
    
    return test1_urls

import pandas as pd

watch_main_url = pd.DataFrame(watch_url_1(),columns=['main_url'])

watch_main_url.to_csv("watch_main_url.csv")
    

            
            
    
        
        
        
        
        
        
        
        
        
        
        
    
    
    
    
    




