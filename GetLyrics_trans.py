import json
import math
import os
import requests
import urllib
import time


# split_s = ' | '
split_s = ' 🎵 '


def str2int(s):
    if len(s.split(':')) < 2:
        return 0
    minn =s.split(':')[0]
    sec = s.split(':')[1]
    try:
        res = 60 * int(minn) + float(sec)
    except:
        return 0
    return res


def int2str(n):
    n = float(n)
    minn = int(n // 60)
    sec = math.floor(n - minn * 60)
    other = n - minn * 60 - sec
    res = "%02d:%02d.%s" % (minn, sec, str("%02d0" % int(other * 100)))
    return res


li = os.listdir()

name = []
for i in li:
    if '.mp3' in i:
        name.append(i.split('.mp3')[0])

ids = []
items = {}

for key in name:
    time.sleep(2)
    try:
        print('search:', key, end='')
        url = 'https://v1.hitokoto.cn/nm/search/%s?type=SONG&offset=0&limit=3' % urllib.parse.quote(key)
        js = requests.get(url, timeout=10).text
        js = json.loads(js)
        if not js['code'] == 200:
            print(js['code'])
            continue
        songs = js['result']['songs']
        ids.append(songs[0]['id'])
        items[songs[0]['id']] = key
        print('...done')
    except Exception as e:
        print('...search', key, 'time out')
        continue

retry = 0

for k in ids:
    time.sleep(2)
    print('get:', items[k], end=' ')
    lrc_url = 'https://v1.hitokoto.cn/nm/lyric/%d' % k
    try:
        lrc_js = json.loads(requests.get(lrc_url, timeout=10).text)
        lrc = lrc_js['lrc']['lyric']
        if 'lyric' not in lrc_js['tlyric']:
            with open(items[k] + '.lrc', 'w', encoding='utf-8') as f:
                f.write(lrc)
            print('...done')
            continue
        tlrc = lrc_js['tlyric']['lyric']
    except Exception as e:
        print('Error,', e, 'retry:', retry)
        retry = retry + 1
        continue

    li1 = lrc.split('\n')
    dat = {}
    head = []

    for i in range(len(li1)):
        if len(li1[i].split(']')) < 2:
            continue
        pre = li1[i].split(']')[0][1:]
        res = "%.2f" % str2int(pre)
        if res not in dat:
            dat[res] = li1[i].split(']')[1]

    if tlrc is not None:
        li2 = tlrc.split('\n')
        for i in range(len(li2)):
            if len(li2[i].split(']')) < 2:
                continue
            pre = li2[i].split(']')[0][1:]
            res = "%.2f" % str2int(pre)
            if res in dat:
                # dat[res] = dat[res] + split_s + li2[i].split(']')[1]
                dat[res] = li2[i].split(']')[1] + split_s + dat[res]
            else:
                dat[res] = li2[i].split(']')[1]

    dat2 = {}
    
    for d in dat:
        s = int2str(d)
        dat2[s] = "%s" % dat[d]

    li = []
    for d in dat2:
        li.append(d)
    li.sort()

    result = ''
    for i in li:
        result = result + "[%s]%s\n" % (i, dat2[i])
    
    with open(items[k] + '.lrc', 'w', encoding='utf-8') as f:
        f.write(result)
    print('...done')
