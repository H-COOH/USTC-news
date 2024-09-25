import hashlib
import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"}

res=[]  # id hash src url text time main

def insert(dat):
	sha256_hash=hashlib.sha256()
	sha256_hash.update(str(dat).encode("utf-8"))
	res.append([sha256_hash.hexdigest()]+dat)

def get_text(t):
	while t and t[0] in [" ","\t","\n","\r"]: t=t[1:]
	while t and t[-1] in [" ","\t","\n","\r"]: t=t[:-1]
	return t

def get_home(p):
	url="https://www.ustc.edu.cn/tzgg/{}.htm".format(p)
	soup=BeautifulSoup(requests.get(url=url,headers=headers).content.decode("utf-8"),"lxml")
	data=soup.find_all("tr",class_="light")
	for i in data:
		u=i.contents[3].contents[1]
		insert([p,urljoin(url,u["href"]),u.text,i.contents[5].text,"请点击链接以查看详细内容"])

def get_teach():
	url="https://www.teach.ustc.edu.cn/category/notice"
	soup=BeautifulSoup(requests.get(url=url,headers=headers).text,"lxml")
	data=soup.find_all("li",class_="type-post")
	for i in data:
		u=i.contents[3].contents[0]
		r=requests.get(url=u["href"],headers=headers)
		if u["href"].find("https://www.teach.ustc.edu.cn/") or r.status_code!=200:
			s="请点击链接以查看详细内容"
		else:
			s=BeautifulSoup(r.text,"lxml").find("article").text
		insert(["teach",u["href"],u.text,get_text(i.contents[5].text),get_text(s)])

def get_ysjt():
	url="https://ysjt.ustc.edu.cn/18033/list.htm"
	soup=BeautifulSoup(requests.get(url=url,headers=headers).content.decode("utf-8"),"lxml")
	data=soup.find("table",class_="wp_article_list_table").contents
	for i in range(1,len(data),2):
		u=data[i].contents[1].contents[1].contents
		t=get_text(u[3].text)
		u=u[1].contents[1]
		k=urljoin(url,u["href"])
		s=BeautifulSoup(requests.get(url=k,headers=headers).content.decode("utf-8"),"lxml").find(class_="wp_articlecontent").text
		insert(["ysjt",k,get_text(u.text),t,get_text(s.replace(u"\xa0"," "))])

def get_math():
	url="https://math.ustc.edu.cn/bzxs/list.htm"
	soup=BeautifulSoup(requests.get(url=url,headers=headers).content.decode("utf-8"),"lxml")
	data=soup.find("ul",class_="wp_article_list").contents
	for i in range(1,len(data),2):
		u=data[i].contents[1].contents[3].contents[0]
		k=urljoin(url,u["href"])
		s=BeautifulSoup(requests.get(url=k,headers=headers).content.decode("utf-8"),"lxml").find(class_="wp_articlecontent").text
		insert(["math",k,u.text,get_text(data[i].contents[3].text),get_text(s.replace(u"\xa0"," "))])

get_home("jxltz")
get_home("glltz")
get_home("fwltz")
get_teach()
get_ysjt()
get_math()

re=requests.post(url="https://fun.mzxr.top/info/update.php",json={"token":sys.argv[1],"data":res}).text
print(re)
