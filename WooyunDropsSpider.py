#/usr/bin/env python
#!encoding=UTF-8
'''
   采集wooyun知识库文章的脚本，改自Tools上。
   修改时间：2015-12-20
   修改作者: cf_hb 
'''
import urllib2
import requests
import re
import sys
import hashlib
import math
import threading
import time
import os
reload(sys)
sys.setdefaultencoding("utf-8" )

#默认保存文件夹
FileName = "drops"
#默认使用30个线程
ThreadNum  = 30
#采集网站地址
SiteUrl = "http://drops.wooyun.org/"
#线程队列
threads = []
#总页数
TotalPage = 0
#所有列表页面URL
PageListUrls = []
#所有文章URL
PageUrls = []
#文章内容
Articles = []

#获取总页数
def get_total_page_number(url):
    patt = re.compile(r"class='nextpostslink'>&raquo;</a><a href='http://drops.wooyun.org/page/(.*?)' class='last'>.*?</a>")
    content = requests.get(url)
    total = patt.findall(content.text)
    print 'Success get total number:[{0}]'.format(total[0])
    return int(total[0])

#所有列表页面URL
def get_page_list_url(TotalPage):
    PageListUrls = []
    for i in range(TotalPage):
        PageListUrls.append('http://drops.wooyun.org/page/%d' % i)
    return PageListUrls

#采集文章链接
def get_article_url(PageListUrls):
    PageUrls = []
    for url in PageListUrls:
        patt = re.compile(r"<h2 class=\"entry-title\"><a href=\"(.*?)\" rel=\"bookmark\" title=\".*?\">.*?</a></h2>")
        content = requests.get(url)
        article = patt.findall(content.text)
        for aurl in article:
            PageUrls.append(aurl)
    return PageUrls


#采集文章内容并且缓存本地
def get_article_content(PageUrls):
    for url in PageUrls:
        #抓取页面
        req = requests.get(url)
        content = req.text
        #获取标题
        patt_title = re.compile(r"<h1 class=\"entry-title ng-binding\">(.*?)</h1>")
        title = patt_title.findall(content)
        #获取作者
        path_author = re.compile(r"<a href=\"/author/.*?\" class=\"title ng-binding\">(.*?)</a>")
        author = path_author.findall(content)
        #获取文章内容
        path_section = re.compile(r"<section class=\"entry-content ng-binding\" ng-bind-html=\"postContentTrustedHtml\">([\w\W]*?)</section>")
        section = path_section.findall(content)
        #将采集数据缓存本地
        cache_Articles(url,title[0],author[0],section[0])
        

#将采集数据缓存本地 \/:*?"><|
def cache_Articles(url,title, author, content):
    global FileName
    try:
        filename = title.decode("UTF-8").encode('GBK')+".html"
    except Exception,e:
        try:
            filename = title.decode("UTF-8").encode('UTF-8')+".html"
        except Exception,e2:
            print "e2 = "+e2
            exit(-1)
            
#这里替换文章名中一些不能写做文件名的特殊符号
    filename = filename.replace("\\",".")
    filename = filename.replace("&nbsp;"," ")
    filename = filename.replace("/",".")
    filename = filename.replace(":",".")
    filename = filename.replace("*",".")
    filename = filename.replace("?",".")
    filename = filename.replace("\"",".")
    filename = filename.replace("<",".")
    filename = filename.replace(">",".")
    filename = filename.replace("|",".")
    filename = filename.replace("'","\\'")
#保存在当前目录的drops文件夹下面
    filename = FileName+"/"+filename
    print "Successed Downloading >> "+filename
    try:
        fw = open(filename,"w+")
    except Exception,e:
    	#用文章的名字创建文件失败时，使用当前时间创建html文件
        Fname =FileName+"/"+str(int(time.time()))+".html" 
        fw = open(Fname,'w+')
    try:
        text = '''
        <html>
			<head>
			     <title>${title}$ - ${author}$</title>
				 <meta http-equiv="content-type" content="text/html; charset=UTF-8">
			</head>
			<body>
				<h1>原文地址:<a href="${url}$">${url}$</a></h1>
				${content}$
			</body>
		</html>
        '''
        s = text.replace('${url}$',str(url)).replace('${title}$',str(title)).replace('${author}$',str(author)).replace('${content}$',str(content))
        fw.write(s)
    except Exception,e:
        #print e
        print "here"
    finally:
        fw.close()
def main():
    global ThreadNum
    global SiteUrl
    global threads
    global TotalPage
    global PageListUrls
    global PageUrls
    global Articles


    #获取总页数
    TotalPage = get_total_page_number( SiteUrl )

    #构建列表页面URL
    PageListUrls = get_page_list_url(TotalPage)

    #采集文章链接
    PageUrls = get_article_url(PageListUrls)

    #获取每个线程执行条数
    ThreadExceNum = math.ceil( len(PageUrls) / ThreadNum  )
    #分组
    PageUrlGroup = []
    #创建目录
    global FileName
    try:
        os.makedirs("drops")
    except:
        print u"drops文件夹创建失败！"
        FileName = str(int(time.time()))
        print u"创建目录"
        os.makedirs(FileName)

    j = 0

    for i in range(0,len(PageUrls)):

        if j % ThreadExceNum == 0:
            #加入线程
            t1 = threading.Thread(target=get_article_content,args=(PageUrlGroup,))
            threads.append(t1)
            PageUrlGroup = []
        else:
            PageUrlGroup.append(PageUrls[i])
        j = j + 1

    for t in threads:
        try:
            t.setDaemon(True)
            t.start()
        except Exception,ex:
            print "something error!"

    t.join()
    print "All Done!!!"
if __name__ == '__main__':
    main()
