import requests, re
import pandas as pd

df = pd.read_csv('watchurl2.csv')

def final_data(urls):
    i=5658
    
    for url in urls:
        # watch_namel = []
        # pricel = []
        # brandl = []
        # modell = []
        # ref_numl = []
        # statel = []
        # movementl = []
        # housingl = []
        # strap_materiall = []
        # manufacture_yearl = []
        # content_deliveredl = []
        # sexl = []
        # locationl = []
        # urll=[]
        url=str(url)+'?SETLANG=en_GB&SETCURR=EUR'
        #url = 'https://www.chrono24.fr/rolex/bubble-back-3131-in-rose-gold-with-turtle-shell-bracelet--id12545987.htm'
        # brand = 'rolex'
        # model = 'bubble-back'

        headers = {
            'authority': 'www.chrono24.fr',
            'cache-control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        #     'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        }

        response = requests.get(str(url), headers=headers)
        resp = response.text

        watch_name = ''
        price = ''
        brand = ''
        model = ''
        ref_num = ''
        manufacture_year = ''
        content_delivered = ''
        sex = ''
        location = ''


        ref_num_re = re.search(r"(?s)<td><strong>Reference number</strong></td>\s+<td>(.*?)</td>",str(resp))
        if ref_num_re:
            ref_num = ref_num_re.group(1)
            ref_num = re.sub(r"'",r"'''",re.sub(r"\s\s+",r" ",re.sub(r"(?s)<.*?>",r"",str(ref_num))))

        watch_name_re = re.search(r'(?s)<h1 class=".*?">(.*?)</h1>',str(resp))
        if watch_name_re:
            watch_name = watch_name_re.group(1)
            watch_name = re.sub(r"'",r"'''",re.sub(r"\s\s+",r" ",str(watch_name)))

        price_re = re.search(r'(?s)<span class="price-lg">.*?<span class="">(.*?)</span>',str(resp))
        if price_re:
            price = price_re.group(1)
            price = re.sub(r"'",r"''",re.sub(r"&nbsp;",r" ",re.sub(r"<.*?>",r"",str(price))))
            
        brand_re = re.search(r'(?s)<td><strong>Brand</strong></td>.*?title="(.*?)"',str(resp))
        if brand_re:
            brand = brand_re.group(1)
            brand = re.sub(r"'",r"''",str(brand))
            
            
        model_re = re.search(r'(?s)<td><strong>Model</strong></td>.*?title="(.*?)"',str(resp))
        if model_re:
            model = model_re.group(1)
            model = re.sub(r"'",r"''",str(model))
            
        manufacture_year_re =  re.search(r"(?s)<strong>Year of production</strong></td>\s+<td>\s+(.*?)</td>",str(resp))
        if manufacture_year_re:
            manufact_year = manufacture_year_re.group(1)
            manufact_year = re.sub(r"'",r"''",re.sub(r"\s\s+",r" ",re.sub(r"<.*?>",r"",str(manufact_year))))
            
            if 'Unknown' in manufact_year:
                manufacture_year = 'Unknown'
            else:
                if re.search(r'(\d+)',str(manufact_year)):
                    manufacture_year = re.search(r'(\d+)',str(manufact_year)).group(1)
                else:
                    manufacture_year = ''    
            

        content_delivered_re = re.search(r'(?s)<strong>Scope of delivery</strong></td>\s+<td>(.*?)<i\s+class=',str(resp))
        if content_delivered_re:
            content_delivered = content_delivered_re.group(1)
            content_delivered = re.sub(r"'",r"''",re.sub(r"\s\s+",r" ",re.sub(r"<.*?>",r"",str(content_delivered))))
            
        sex_re = re.search(r'(?s)<strong>Gender</strong></td>\s+<td>(.*?)</td>',str(resp))
        if sex_re:
            sex = sex_re.group(1)
            sex = re.sub(r"'",r"''",re.sub(r"\s\s+",r" ",re.sub(r"<.*?>",r"",str(sex))))
            
        location_re = re.search(r'(?s)<strong>Location</strong></td>\s+<td>(.*?)</td>',str(resp))
        if location_re:
            location = location_re.group(1)
            location = re.sub(r"'",r"''",re.sub(r"\s\s+",r" ",re.sub(r"<.*?>",r"",str(location))))       

        
        print(i)  
                  
        print ("brand:",brand)
        print ("model:",model)
        print ("watch_name:",watch_name)
        print ("price:",price)
        print ("ref_num:",ref_num)
        # print ("movement:",movement)
        # print ("housing:",housing)
        # print ("strap_material:",strap_material)
        print ("manufacture_year:",manufacture_year)
        # print ("state:",state)
        # print ("content_delivered:",content_delivered)
        print ("sex:",sex)
        print ("location:",location)
        print ("source_url:",url)

        # watch_namel.append(watch_name)
        # pricel.append(price)
        # brandl.append(brand)
        # modell.append(model)
        # ref_numl.append(ref_num)
        # statel.append(state)
        # movementl.append(movement)
        # housingl.append(housing)
        # strap_materiall.append(strap_material)
        # manufacture_yearl.append(manufacture_year)
        # content_deliveredl.append(content_delivered)
        # sexl.append(sex)
        # locationl.append(location)
        # urll.append(url)

        main_url3 = pd.DataFrame({'Brand':brand,'Model':model,'Reference Number':ref_num,'Watch Name':watch_name,'Price':price,
        'Year Of Production':manufacture_year,'Scope of delivery':content_delivered,'Gender':sex,
        'Location':location,'Source Url':url},index=[i])

        i=i+1

        main_url3.to_csv("Final_Data_Watches.csv",mode='a',header=False)

    return "Datas stored Successfully"
#watch_namel,pricel,brandl,modell,ref_numl,statel,movementl,housingl,strap_materiall,manufacture_yearl,content_deliveredl,sexl,locationl

link_1 = df.Watch_link[5658:]
import pandas as pd
#watch_namel,pricel,brandl,modell,ref_numl,statel,movementl,housingl,strap_materiall,manufacture_yearl,content_deliveredl,sexl,locationl=final_data(link_1)

print(final_data(link_1))

# main_url3 = pd.DataFrame({'watch_name':watch_namel,'price':pricel,'brand':brandl,'model':modell,'ref_num':ref_numl,'state':statel,
# 'movement':movementl,'housing':housingl,'strap_material':strap_materiall,'manufacture_year':manufacture_yearl,'content_delivered':content_deliveredl,'sex':sexl,
# 'location':locationl})






