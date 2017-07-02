#coding:utf-8
import requests
import gevent
from gevent import monkey
from lxml import etree
import urlparse
import sys
import re

monkey.patch_all()

#域名
domain="qdedu.net"
#target
base_url="http://www.qd28.qdedu.net"
exp_url=set()
defeated_url=[]
url_dict={}
post_url=[]

def requ(url):
    jobs=[]
    if url in exp_url:
        return
    else:
        exp_url.add(url)
    try:
        req = requests.get(url,timeout=10)
        print "GET:%s"%url
        if req.status_code==200:
            select=etree.HTML(req.content)
            links=select.xpath("//a/@href")
            for link in links:
                if link=="":continue
                tmp=urlparse.urlsplit(link)
                if tmp.scheme in ['http','https']:
                    jobs.append(gevent.spawn(pasd,tmp,link))
                else:
                    link=base_url+link if link[0]=="/" else base_url+"/"+link
                    pasd(tmp,link)
                    jobs.append(gevent.spawn(pasd,tmp,link))
            gevent.joinall(jobs)
            for i in post_url:
                print i
    except Exception,e:
        print "ERROR",e
        defeated_url.append(url)

def pasd(tmp,link):
    path=tmp.path
    if domain in link:
        if "?" in link:
            try:
                if path[0]=='/':
                    path=path[1:]
                if path in url_dict:
                    if '.html' or '.htm' in tmp.query:return
                    else:
                        for udt in url_dict[path]:
                            if udt == sorted([re.sub(r'\=.+', '', i) for i in tmp.query.split("&")]):return
                            else:
                                url_dict[path].append(sorted([re.sub(r'\=.+', '', i) for i in tmp.query.split("&")]))
                                post_url.append(link)
                                requ(link)
                else:
                    if '.html' in tmp.query or '.htm' in tmp.query:
                        url_dict[path]=''
                        post_url.append(link)
                        requ(link)
                    else:
                        url_dict[path]=sorted([re.sub(r'\=.+', '', i) for i in tmp.query.split("&")])
                        post_url.append(link)
                        requ(link)
            except:
                defeated_url.append(link)
        else:
            requ(link)


if __name__ == '__main__':
    try:
        if len(sys.argv)<3:
            print u"请输入 domain target   python getPostUrl baidu.com http://www.baidu.com\n"
        else:
            domain,base_url=sys.argv[1],sys.argv[2]
            requ(base_url)
            print u"包含数据交互的链接",post_url
            print u"所有成功访问到的链接",exp_url
            print u"未成功访问到的链接",defeated_url
    except:
        print u"包含数据交互的链接",post_url
        print u"所有成功访问到的链接",exp_url
        print u"未成功访问到的链接",defeated_url

