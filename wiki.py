from bs4 import BeautifulSoup
import lxml
import requests
import time
import re
import os
import urllib.request
import sys
import datetime
import threading
import linecache


class DownloadThread(threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run(self):
        main(self.name)


urlbase = 'https://en.wikipedia.org'
resume_lock = threading.Lock()
res = 0
retry = 0


# Get html
def getHtml(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.2372.400 QQBrowser/9.5.10548.400'
        ,
        'Cookie': 'bid=I0klBiKF3nQ; ll="118277"; gr_user_id=ffdf2f63-ec37-49b5-99e8-0e0d28741172; ap=1; _vwo_uuid_v2=8C5B24903B1D1D3886FE478B91C5DE97|7eac18658e7fecbbf3798b88cfcf6113; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1498305874%2C%22https%3A%2F%2Fbook.douban.com%2Ftag%2F%25E9%259A%258F%25E7%25AC%2594%3Fstart%3D20%26type%3DT%22%5D; _pk_id.100001.4cf6=4e61f4192b9486a8.1485672092.5.1498306809.1498235389.; _pk_ses.100001.4cf6=*'
    }
    req = requests.get(url, headers)
    return req.text


#################################################################
# FunctionName:    getImage(html,mstring)
# Function:
# Input:           html:html code;
# output:          Imgsrc:Picture Download Address;
# Modifiction:     2018.5.7
#################################################################

def getImage(html):
    soup = BeautifulSoup(html, 'lxml')
    Pendingstr = soup.find('div', id='bodyContent')
    Pendingstr2 = Pendingstr.find('div', id='mw-content-text')
    Pendingstr3 = Pendingstr2.find('table', class_=re.compile('^(?=.*?infobox)(?=.*?vcard).+$'))
    Securl = Pendingstr3.find('a', href=re.compile('^(?=.*?File:)(?!.*?\.svg).+$'))['href']
    Securl = urlbase + Securl
    Sechtml = getHtml(Securl)
    Secsoup = BeautifulSoup(Sechtml, 'lxml')
    Pendingstr4 = Secsoup.find('div', id='content')
    Pendingstr5 = Pendingstr4.find('div', id='bodyContent')
    Pendingstr6 = Pendingstr5.find('div', id='mw-content-text')
    Pendingstr7 = Pendingstr6.find('div', class_='fullMedia')
    ImgSrc = Pendingstr7.find('a')['href']
    return ImgSrc


#################################################################
# FunctionName:   IsMatch(string,mstring)
# Function:       Match Test Function
# Input:          string:Pending string
#                 mstring:Regular expression
# output:         match:Matching results
# Modifiction:    2018.5.7
#################################################################
def IsMatch(string, mstring):
    pattern = re.compile(mstring)
    match = pattern.search(string)
    return match


#################################################################
# FunctionName:   ListTransString(List)
# Function:       List trans to string
# Input:          List:Pending list
# output:         match:string
# Modifiction:    2018.5.7
#################################################################
def ListTransString(List):
    str1 = ""
    for i in range(0, List.__len__()):
        List[i] = str(List[i])
    str1 = str1.join(List)
    return str1


# Get matching string
def GetReString(string, mstring):
    pattern = re.compile(mstring)
    string = ListTransString(pattern.findall(string))
    return string


# once log with datetime
def Recordlog(logname, str, method='a'):
    with open('./' + logname + '.txt', method) as log:
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(nowTime + '\t\t' + str + '\n')


# Try Download
def TryDownload(url, id):
    global retry
    try:
        html = getHtml(url)
        Imagesrc = getImage(html)
        DownLoadPic(Imagesrc, './pic/' + id, id)

    except (TypeError, AttributeError) as Argument:
        Imagesrc = ''
        Recordlog('errlog', 'errlog:\t' + id + '\tNot Found')

    except:
        Imagesrc = ''
        Argument = sys.exc_info()
        Recordlog('errlog', 'errlog:\t' + id + '\t' + str(Argument))
        if retry < 5:
            time.sleep(3)
            retry = retry + 1
            TryDownload(url, id)
        else:
            Recordlog('errlog', 'errlog:\t' + id + '\tFailed for\t' + str(Argument))
            time.sleep(10)
            retry = 0
    return Imagesrc


# Download picture function
def DownLoadPic(img_url, img_pos, picname):
    id = picname

    pic_suffix = os.path.splitext(img_url)[1]
    if pic_suffix != '.jpg' and pic_suffix != '.JPG':
        with open('./suffix.txt', 'a', encoding='utf-8') as suf:
            suf.write(pic_suffix + '\n')
    picname = '{}{}{}{}'.format(img_pos, os.sep, picname, pic_suffix)
    if not os.path.exists(img_pos):
        os.makedirs(img_pos)
    urllib.request.urlretrieve('https:' + img_url, filename=picname)


def getresumeinfo():
    with open('./resume.txt', 'r', encoding='utf-8') as ress:
        fcount = ress.readline()
        if '' != fcount:
            fcount = int(fcount)
        else:
            fcount = 1
        return fcount


def main(threads):
    global res
    count = 1
    fplen = len(open('./90Wid&name.txt', 'rU', encoding='utf-8').readlines())

    with open('./90Wid&name.txt', 'r', encoding='utf-8') as fp:
        for PendingRead in fp:
            fcount = getresumeinfo()
            if count < fcount:
                count += 1
                continue
            # lock
            resume_lock.acquire()
            fcount = getresumeinfo()
            if count >= fcount:
                with open('./resume.txt', 'w', encoding='utf-8') as resume:
                    resume.write(str(int(fcount) + 1))
            resume_lock.release()
            # release
            if count >= fcount:
                id = GetReString(PendingRead, '^.*?(?=\s)')
                name = GetReString(PendingRead, '(?<=\s\s).*?$')
                # Name = Name.strip('"')
                namee = name.replace(' ', '_')
                url = urlbase + '/wiki/' + namee

                Imagesrc = TryDownload(url, id)

                if Imagesrc != '':
                    with open('./Imgurl.txt', 'a', encoding='utf-8') as Imgurl:
                        Imgurl.write(id + ':\t\t' + Imagesrc + '\n')

                nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                print(nowTime + '\t\t' + str(count) + '/' + str(fplen) + ' finished' + '\t\t' + threads)
                count = count + 1
                time.sleep(1)

            else:
                count += 1


def resumede():
    with open('./resume.txt', 'r', encoding='utf-8') as resume:
        count = resume.readline()
    with open('./resume.txt', 'w', encoding='utf-8') as resume:
        resume.write(str(int(count) - 5))


if __name__ == "__main__":
    resumede()
    thread1 = DownloadThread(1, 'Thread-1')
    thread2 = DownloadThread(2, 'Thread-2')
    thread3 = DownloadThread(3, 'Thread-3')
    thread4 = DownloadThread(4, 'Thread-4')
    thread5 = DownloadThread(5, 'Thread-5')

    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()
