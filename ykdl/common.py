#!/usr/bin/env python
# -*- coding: utf-8 -*-

from importlib import import_module

from .util.match import match1
from .util.html import fake_headers

def mime_to_container(mime):
    mapping = {
        'video/3gpp': '3gp',
        'video/mp4': 'mp4',
        'video/webm': 'webm',
        'video/x-flv': 'flv',
    }
    if mime in mapping:
        return mapping[mime]
    else:
        return mime.split('/')[1]

alias = {
        '163': 'netease',
        'fun': 'funshion',
        'iask': 'sina',
        'in': 'alive',
        'kankanews': 'bilibili',
        'smgbb': 'bilibili',
        '7gogo': 'nanagogo'
}
def url_to_module(url):
    video_host = match1(url, 'https?://([^/]+)/')
    video_url = match1(url, 'https?://[^/]+(.*)')
    assert video_host and video_url, 'invalid url: ' + url

    if video_host.endswith('.com.cn'):
        video_host = video_host[:-3]
    domain = match1(video_host, '(\.[^.]+\.[^.]+)$') or video_host
    assert domain, 'unsupported url: ' + url

    k = match1(domain, '([^.]+)')
    if k in alias.keys():
        k = alias[k]
    try:
        m = import_module('.'.join(['ykdl','extractors', k]))
        if hasattr(m, "get_extractor"):
            site = m.get_extractor(url)
        else:
            site = m.site
        return site, url
    except(ImportError):
        from ykdl.compact import HTTPConnection
        conn = HTTPConnection(video_host)
        conn.request("HEAD", video_url, headers=fake_headers)
        res = conn.getresponse()
        location = res.getheader('location')
        if location is None:
            return import_module('ykdl.extractors.generalembed').site, url
        elif location != url:
            return url_to_module(location)
        else:
            raise ConnectionResetError(url)
