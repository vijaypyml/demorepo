import requests,re

url = 'https://www.chrono24.co.uk/rolex/air-king-ref114234--id16533347.htm?SETLANG=en_GB&SETCURR=EUR'
# url = 'https://www.chrono24.co.uk/rolex/montre-rolex-air-king-en-acier-ref--114200-vers-2008--id15927357.htm?SETLANG=en_GB&SETCURR=EUR'
# url = 'https://www.chrono24.co.uk/rolex/air-king-ref114234--id16533347.htm?SETLANG=en_GB&SETCURR=EUR'


headers = {
    'authority': 'www.chrono24.co.uk',
    'cache-control': 'max-age=0',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
#     'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#     'cookie': '__cfduid=df1e8f9f0b3e57a267ff17237d6b5b4971601140404; c24userprefs=SETLANG%3Den_GB%26SETCURR%3DEUR; chronosessid=ff0cddec-bcd1-4298-ad05-e8b2607b93d1; csrf-token=1601140404.WSzSM8e1owMe1F5B83jDQZeOYJRl48og5ma2KlhVtFQ.AXG1VdhMeh1K_eV5433KMkHYkOU2; __Host-csrf-token=1601140404.WSzSM8e1owMe1F5B83jDQZeOYJRl48og5ma2KlhVtFQ.AXG1VdhMeh1K_eV5433KMkHYkOU2; timezoneOffset=-330; __gads=ID=f504d94fa18d4e63:T=1601140409:S=ALNI_MY9Rj_4kJmiYEMl8Il3FbHs59tgmw; c24-consent=AAAAGO//wQE=; _gid=GA1.3.1156678655.1601140414; cfctGroup=CTRB01%3D%26SIMI00%3D%26FOBRO00%3D%26WCDS00%3D%26FAQ00%3D; _fbp=fb.2.1601140670340.2057687500; _hjTLDTest=1; _hjid=ae142ec3-400a-4c7f-a8d1-f99473ef9cbc; _hjIncludedInPageviewSample=1; _hjAbsoluteSessionInProgress=0; _ga=GA1.1.1042720531.1601140409; _ga_PS820NHZPE=GS1.1.1601140413.1.1.1601141137.60; c24-data=eyI1Ijp7ImUiOiIxNjAzNzMyNjY2IiwidiI6IjQifSwiNiI6eyJlIjoiMTYwMzczMjY2NiIsInYiOiIxIn0sIjI1Ijp7InYiOiJhNmU4MTI3NmQzLDZkMDZjNDU4YzYsN2IwYmVjZmY3Nyw2MTk0YjZiM2NkLDFlZjY1YmM5ZDYsZjY0ODgyYTU0OCxiZjYyODQ5MGU0LDA1ZjkwY2RmYmYsOTg2ZTFkYzJkNSxhMTEzNTJmNTZhIiwiZSI6IjE2MDM3MzI2NjkifSwiMjciOnsiZSI6IjE2MzI2NzY0MDQiLCJ2IjoiMSJ9LCIzNiI6eyJlIjoiMTYzMjY3NjQwNCIsInYiOiIxNjAxMTQwNDA0MTQ0In0sIjM3Ijp7ImUiOiIxNjMyNjc2NDE0IiwidiI6IjE2MDExNDA0MTQxMDEifSwiMzgiOnsiZSI6IjE2MzI2NzY0MDQiLCJ2IjoiMTU5ODQ2MjAwNDE0NCJ9LCI0MSI6eyJlIjoiMTYzMjY3NjQwNCIsInYiOiIxNjAxMTQwNDA0MDAwIn0sIjU3Ijp7InYiOiI1MmE3NGZhNzEwIiwiZSI6IjE2MDM3MzI2NjkifSwiNjAiOnsiZSI6IjE2MDE3NDUyMDkiLCJ2IjoiMSJ9LCI5OCI6eyJlIjoiMTYzMjY3NjY2NiIsInYiOiI0In0sIjExNSI6eyJ2IjoibGciLCJlIjoiMTYxNjY5NDA3MiJ9LCIxMjUiOnsidiI6IjE2MDExNDA2NjY0NzkiLCJlIjoiMTYwMjQzNjY3MSJ9LCIxMjYiOnsidiI6IjEiLCJlIjoiMTYwMjQzNjY3MSJ9LCIxMjciOnsidiI6IjEiLCJlIjoiMTYwMjQzNzEzNyJ9fQ%3D%3D',
}

params = (
    ('SETLANG', 'en_GB'),
    ('SETCURR', 'EUR'),
)

response = requests.get(url, headers=headers, params=params)
resp = response.text

watch_name = ''
price = ''
brand = ''
model = ''
ref_num = ''
state = ''
movement = ''
housing = ''
strap_material = ''
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

    
# print ("brand:",brand)
# print ("model:",model)
# print ("ref_num:",ref_num)
# print ("watch_name:",watch_name)
# print ("price:",price)
# print ("Year_production:",manufacture_year)
# print ("Scope of delivery:",content_delivered)
# print ("Gender:",sex)
# print ("Location:",location)
# print ("source_url:",url)