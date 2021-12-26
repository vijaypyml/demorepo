import requests, re
import pandas as pd
# from chrono_test import watch_url_1 as main_url

df = pd.read_csv('watch_main_url.csv')
# print (df)
 
def watch_url_2(urls):
    watch_url_2 = []
    for url in urls:
        print ("url:",url)
        headers = {
            'authority': 'www.chrono24.fr',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
            'referer': str(url),
        #     'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }
         
        response = requests.get(str(url), headers=headers)
        resp = response.text
         
#         link_re = re.search(r'(?s)(<span class="active">.*?<li class="flex-grow">)',str(resp))
#         if link_re:
#             link = link_re.group(1)
#             for pages in re.finditer(r'(?s)<a href=".*?".*?>\s+(\d+)</a>',str(link)):
#                 page_num = pages.group(1)
#                 page_num = int(page_num)+1
                 
#             print ("page_num:",page_num)
             
        for i in range(1,3,1):
            print (i)
            hit_link = re.search(r'(.*?)\.htm',str(url)).group(1)
            h_link = str(hit_link)+"-"+str(i)+".htm"
             
            headers = {
                'authority': 'www.chrono24.fr',
                'cache-control': 'max-age=0',
                'upgrade-insecure-requests': '1',
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
                'referer': str(url),
    #             'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            }
             
            response2 = requests.get(str(h_link), headers=headers)
            resp2 = response2.text
             
            w_link_re = re.search(r'<div class="article-item-container">\s+<a href="(.*?)"',str(resp2))
            if w_link_re:
                for watch_link_re in re.finditer(r'<div class="article-item-container">\s+<a href="(.*?)"',str(resp2)):
                    watch_link = watch_link_re.group(1)
                    watch_link = 'https://www.chrono24.fr'+str(watch_link)
                    watch_link = re.sub(r"'",r"''",str(watch_link))
                    print ("watch_link:",watch_link)
                    watch_url_2.append(watch_link)
#                     print ("brand:",brand)
#                     print ("model:",model)
#                     print("*"*90)
                      
#                     print ("*"*90)
     
    return watch_url_2
                 
 

link_1 = df.main_url
import pandas as pd
 
main_url2 = pd.DataFrame(watch_url_2(link_1),columns=['Watch_link'])
main_url2.to_csv("watchurl2.csv")





