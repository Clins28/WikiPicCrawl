from bs4 import BeautifulSoup
import lxml
import requests
import time
import re
import os
import urllib.request
import sys
import datetime

urlbase = 'https://en.wikipedia.org'


count = 1
res = 0
retry = 0

#Get html
def getHtml(url):
	headers = {
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400'
		,
		'Cookie': 'bid=I0klBiKF3nQ; ll="118277"; gr_user_id=ffdf2f63-ec37-49b5-99e8-0e0d28741172; ap=1; _vwo_uuid_v2=8C5B24903B1D1D3886FE478B91C5DE97|7eac18658e7fecbbf3798b88cfcf6113; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1498305874%2C%22https%3A%2F%2Fbook.douban.com%2Ftag%2F%25E9%259A%258F%25E7%25AC%2594%3Fstart%3D20%26type%3DT%22%5D; _pk_id.100001.4cf6=4e61f4192b9486a8.1485672092.5.1498306809.1498235389.; _pk_ses.100001.4cf6=*'
	}
	req = requests.get(url,headers)
	return req.text
	
#################################################################
#FunctionName:	getImage(html,mstring)
#Function:		
#Input:			html:html code;
#output:		Imgsrc:Picture Download Address;
#Modifiction:	2018.5.7
#################################################################

def getImage(html):
	soup = BeautifulSoup(html, 'lxml')
	Pendingstr = soup.find('div', id = 'bodyContent')
	Pendingstr2 = Pendingstr.find('div', id = 'mw-content-text')
	Pendingstr3 = Pendingstr2.find('table', class_ = re.compile('^(?=.*?infobox)(?=.*?vcard).+$'))
	Securl = Pendingstr3.find('a', href = re.compile('^(?=.*?File:)(?!.*?\.svg).+$'))['href']
	Securl = urlbase + Securl
	Sechtml = getHtml(Securl)
	Secsoup = BeautifulSoup(Sechtml, 'lxml')
	Pendingstr4 = Secsoup.find('div', id = 'content')
	Pendingstr5 = Pendingstr4.find('div', id = 'bodyContent')
	Pendingstr6 = Pendingstr5.find('div', id = 'mw-content-text')
	Pendingstr7 = Pendingstr6.find('div', class_ = 'fullMedia')
	ImgSrc = Pendingstr7.find('a')['href']
	return ImgSrc
	
#################################################################
#FunctionName:	IsMatch(string,mstring)
#Function:		Match Test Function
#Input:			string:
#				mstring:
#output:		match:
#Modifiction:	2018.5.7
#################################################################
def IsMatch(string,mstring):
	pattern = re.compile(mstring)
	match = pattern.search(string)
	return match

#List trans to string
def ListTransString(List):
	str1 = ""
	for i in range(0,List.__len__()):
		List[i] = str(List[i])
	str1 = str1.join(List)
	return str1
	
#Get matching string
def GetReString(string,mstring):
	pattern = re.compile(mstring)
	string = ListTransString(pattern.findall(string))
	return string
	
#Try Download
def TryDownload(url,id):
	global retry
	with open('./errlog.txt', 'a', encoding='utf-8') as errlog:
		try:
			html = getHtml(url)
			Imagesrc = getImage(html)
			DownLoadPic(Imagesrc, './pic/' + id, id)
		
		except (TypeError,AttributeError) as Argument:
			Imagesrc = ''
			errlog.write('errlog:\t' + id + '\tNot Found\n')
			
		except:
			Imagesrc = ''
			Argument=sys.exc_info()
			errlog.write('errlog:\t' + id + '\t' + str(Argument) + '\n')
			if retry < 5:
				time.sleep(3)
				retry = retry + 1
				TryDownload(url,id)
			else:
				errlog.write('errlog:\t' + id + '\tFailed for\t' + str(Argument) + '\n')
				time.sleep(10)
				retry = 0
		return Imagesrc
		
#Download picture function
def DownLoadPic(img_url,img_pos,picname):
	id = picname
			
	pic_suffix = os.path.splitext(img_url)[1]
	if pic_suffix != '.jpg' and pic_suffix != '.JPG':
		with open('./suffix.txt', 'a', encoding='utf-8') as suf:
			suf.write(pic_suffix + '\n')
	picname = '{}{}{}{}'.format(img_pos,os.sep,picname,pic_suffix)
	if not os.path.exists(img_pos):
		os.makedirs(img_pos)
	urllib.request.urlretrieve('https:' + img_url,filename=picname)
		
def main():
	global res
	global count
	with open('./resume.txt', 'r', encoding='utf-8') as ress:
		rid = ress.readline()
		count = ress.readline()
		if '' != count:
			count = int(count)
		else:
			count = 1
		print ('rid = ' + rid)
	with open('./90Wid&name.txt', 'r', encoding='utf-8') as fp:
		for PendingRead in fp:
			if rid == PendingRead or rid == '':
				res = 1
			if res == 1:
				id = GetReString(PendingRead, '^.*?(?=\s)') 
				Name = GetReString(PendingRead, '(?<=\s\s).*?$')
				#Name = Name.strip('"')
				Namee = Name.replace(' ','_')
				url = urlbase + '/wiki/' + Namee
						
				Imagesrc = TryDownload(url,id)
				if Imagesrc != '':
					with open('./Imgurl.txt', 'a', encoding='utf-8') as Imgurl:
						Imgurl.write(id + ':\t\t' + Imagesrc + '\n')
						
				with open ('./resume.txt', 'w', encoding='utf-8') as resume:
					resume.write(PendingRead)
					resume.write(str(count))
					
				nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				print (nowTime + '\t\t' + str(count) + '/20000' + ' finished')
				count = count + 1
				time.sleep(1)

if __name__ == "__main__":
	main()
		

	
	
		