# coding:utf8
import sys
import os
import time
import re
import traceback

import requests
import config

url_list = list()
url = ''
base_dir = ''
special_filename = '.htaccess'


def get_special_file_content(minipath):
    dir = minipath[1:]
    data = {'editfile': special_filename,
            'dir': base_dir + dir}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        msg = "get special file error:" + url + " error code = " + r.status_code
        print msg
        error_log(msg)

    str = re.findall('<textarea name=content cols=122 rows=20>(.*?)</textarea>',  r.content, re.S)

    if len(str) <= 0:
        str[0] = ""

    return str[0]


def ListFilesToTxt(dir, recursion, minipath):
    files = os.listdir(dir)
    for name in files:
        fullname = os.path.join(dir, name)
        print dir, name, 'dd'
        if (os.path.isdir(fullname) & recursion):
            copy_minipath = minipath + '/' + name
            print copy_minipath, 'ds'
            makedir(copy_minipath)
            ListFilesToTxt(fullname, recursion, copy_minipath)
        else:
            content = ""
            if special_filename in fullname:
                content = get_special_file_content(minipath)
            upload_file(minipath, fullname, content)
            pass


def makedir(dir):
    print 'mkdir ' + dir
    data = {'cmd': 'mkdir ' + dir, 'dir': base_dir}
    r = requests.post(url, data=data)
    if r.status_code != 200:
        msg = "mkdir error:" + url + " error code = " + r.status_code + "dir = " +dir
        print msg
        error_log(msg)


def upload_file(minipath, fullpath, content):
    print 'upload file ' + fullpath
    dir = minipath[1:]
    f = open(fullpath, 'rb')
    if content != "":
        ct = ""
        for line in f.readlines():
            ct += line
        data = {'savefile': special_filename,
            'dir': base_dir + dir,
            'content': ct + "\r\n" + content,
            'submit':'Save'}
        r = requests.post(url, data=data)
        if r.status_code != 200:
            msg = "get special file error:" + url + " error code = " + r.status_code
            print msg
            error_log(msg)
        # f2 = open(special_filename, 'wb')
        # f2.write(f.read())
        # f2.close()
        # f2 = open(special_filename, 'ab')
        # f2.write('\r\n' + content)
        # f2.close()
        # f3 = open(special_filename, 'rb')
    else:
        f3 = f
        files = {'userfile': f3}
        data = {'post': 'yes',
                'dir': base_dir + dir}
        r = requests.post(url, files=files, data=data)
        if r.status_code != 200:
            msg = "upload error:" + url + " error code = " + r.status_code + "filename = " + fullpath
            print msg
            error_log(msg)

def make_url_list():
    urls_dir = config.URLS_DIR
    file = open(urls_dir, 'r')
    while True:
        line = file.readline()
        if line:
            line =line.strip()
            url_list.append(line)
        else:
            break
    file.close()


def get_url(domain):
    for url in url_list:
        if domain in url:
            return url
    print 'Error:' + domain + ' not in url list!!!'


def error_log(msg):
    file = open("./log.log", "a")
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    now_time = time.strftime(ISOTIMEFORMAT, time.localtime())
    file.write(now_time + ": " + msg)
    file.close()


def main():
    global url, base_dir
    make_url_list()
    files_dir = config.FILES_DIR

    files = os.listdir(files_dir)
    for name in files:
        print 'strat run floder:' + name
        url = ''
        url = get_url(name)
        if url:
            try:
                r = requests.get(url)
                if r.status_code == 200:
                    str = re.findall('<input type="text" name="installpath" value="(.*?)">', r.text, re.S)
                    base_dir = str[0]
                    print 'url:' + url
                    fullname = os.path.join(files_dir, name)
                    if os.path.isdir(fullname):
                        ListFilesToTxt(fullname, 1, ".")
                else:
                    msg = "get page error: " + url + " error code = " + r.status_code
                    print msg
                    error_log(msg)
            except Exception as e:
                error_log(traceback.format_exc())

        print 'end run floder:' + name

if __name__ == '__main__':
    main()


# redirectMatch 301 ^/pendleton-2012-catalog.htm http://www.babbittswholesale.com/
# redirectMatch 301 ^/accessories.htm http://www.babbittswholesale.com/
# redirectMatch 301 ^/oraibi/ http://www.babbittswholesale.com/about-us.htm