import urllib,urllib2,sys,re,xbmcplugin,socket
import xbmcgui,xbmcaddon,xbmc,base64
import time,datetime,os,urlresolver
import cookielib,unicodedata,HTMLParser
from BeautifulSoup import BeautifulSoup
from htmlentitydefs import name2codepoint as n2cp
from metahandler import metahandlers
from sqlite3 import dbapi2 as database
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon


addon = Addon('plugin.video.OCM', sys.argv)
ADDON = xbmcaddon.Addon(id='plugin.video.OCM')
datapath = addon.get_profile()
grab = metahandlers.MetaData()
socket.setdefaulttimeout(300)# Bloody tvdb - slow or dead
sys.path.append( os.path.join( ADDON.getAddonInfo('path'), 'resources', 'lib' ) )#Thanks to Eldorado:)
from xgoogle.search import GoogleSearch
cookie_path = os.path.join(datapath, 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)

mode = addon.queries['mode']
play = addon.queries.get('play', None)                      
url = addon.queries.get('url', None)                            
linkback = addon.queries.get('linkback', None)
types = addon.queries.get('types', None)


net = Net()
BASE_URL = 'http://oneclickmoviez.com/'


if ADDON.getSetting('visitor_ga')=='':
    from random import randint
    ADDON.setSetting('visitor_ga',str(randint(0, 0x7fffffff)))

VERSION = "0.0.6"
PATH = "OCM v2"            
UATRACK="UA-38450032-1"

def parseDate(dateString):
    try:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
    except:
        return datetime.datetime.today() - datetime.timedelta(days = 1) #force update


def parseDate(dateString):
    try:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
    except:
        return datetime.datetime.today() - datetime.timedelta(days = 1) #force update


def checkGA():

    secsInHour = 60 * 60
    threshold  = 2 * secsInHour

    now   = datetime.datetime.today()
    prev  = parseDate(ADDON.getSetting('ga_time'))
    delta = now - prev
    nDays = delta.days
    nSecs = delta.seconds

    doUpdate = (nDays > 0) or (nSecs > threshold)
    if not doUpdate:
        return

    ADDON.setSetting('ga_time', str(now).split('.')[0])
    APP_LAUNCH()
    
    
    
                    
def send_request_to_google_analytics(utm_url):
    ua='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    import urllib2
    try:
        req = urllib2.Request(utm_url, None,
                                    {'User-Agent':ua}
                                     )
        response = urllib2.urlopen(req).read()
    except:
        print ("GA fail: %s" % utm_url)         
    return response
       
def GA(group,name):
        try:
            try:
                from hashlib import md5
            except:
                from md5 import md5
            from random import randint
            import time
            from urllib import unquote, quote
            from os import environ
            from hashlib import sha1
            VISITOR = ADDON.getSetting('visitor_ga')
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            if not group=="None":
                    utm_track = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmt=" + "event" + \
                            "&utme="+ quote("5("+PATH+"*"+group+"*"+name+")")+\
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
                    try:
                        print "============================ POSTING TRACK EVENT ============================"
                        send_request_to_google_analytics(utm_track)
                    except:
                        print "============================  CANNOT POST TRACK EVENT ============================" 
            if name=="None":
                    utm_url = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
            else:
                if group=="None":
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                else:
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+group+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                                
            print "============================ POSTING ANALYTICS ============================"
            send_request_to_google_analytics(utm_url)
            
        except:
            print "================  CANNOT POST TO ANALYTICS  ================" 
            
            
def APP_LAUNCH():
        if xbmc.getCondVisibility('system.platform.osx'):
            if xbmc.getCondVisibility('system.platform.atv2'):
                log_path = '/var/mobile/Library/Preferences'
                log = os.path.join(log_path, 'xbmc.log')
                logfile = open(log, 'r').read()
            else:
                log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
                log = os.path.join(log_path, 'xbmc.log')
                logfile = open(log, 'r').read()
        elif xbmc.getCondVisibility('system.platform.ios'):
            log_path = '/var/mobile/Library/Preferences'
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
        elif xbmc.getCondVisibility('system.platform.windows'):
            log_path = xbmc.translatePath('special://home')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
        elif xbmc.getCondVisibility('system.platform.linux'):
            log_path = xbmc.translatePath('special://home/temp')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
        else:
            logfile='Starting XBMC (Unknown Git:.+?Platform: Unknown. Built.+?'
        print '==========================   '+PATH+' '+VERSION+'   =========================='
        try:
            from hashlib import md5
        except:
            from md5 import md5
        from random import randint
        import time
        from urllib import unquote, quote
        from os import environ
        from hashlib import sha1
        import platform
        VISITOR = ADDON.getSetting('visitor_ga')
        match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        for build, PLATFORM in match:
            if re.search('12.0',build,re.IGNORECASE): 
                build="Frodo" 
            if re.search('11.0',build,re.IGNORECASE): 
                build="Eden" 
            if re.search('13.0',build,re.IGNORECASE): 
                build="Gotham" 
            print build
            print PLATFORM
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            utm_track = utm_gif_location + "?" + \
                    "utmwv=" + VERSION + \
                    "&utmn=" + str(randint(0, 0x7fffffff)) + \
                    "&utmt=" + "event" + \
                    "&utme="+ quote("5(APP LAUNCH*"+build+"*"+PLATFORM+")")+\
                    "&utmp=" + quote(PATH) + \
                    "&utmac=" + UATRACK + \
                    "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
            try:
                print "============================ POSTING APP LAUNCH TRACK EVENT ============================"
                send_request_to_google_analytics(utm_track)
            except:
                print "============================  CANNOT POST APP LAUNCH TRACK EVENT ============================"
checkGA()



def GETINDEX(url,linkback,types):
    html = GET_HTML(url)
    r = re.compile(r'<h2><a href="(.+?)".+?title=".+?">(.+?)</a>.+?src="(.+?)" alt=', re.DOTALL).findall(str(html))
    for urls, name, img in r:
        name = str(name).decode("utf-8")
        name = name.encode("ascii","ignore")
        totalitems = len(name)
        contextMenuItems = []
        yname=name
        name = re.findall(r'(.+?)(?=\s[0-9]{4}\s)',str(name))
        year = re.findall(r'.+?([0-9]{4}).+?',str(yname))
        year = ''.join(year).strip()
        name = ''.join(name).replace('-',' ').strip()
        if ADDON.getSetting('use_meta') == 'true':
            infoLabels = GET_META(name,year,types)
        if types == 'movie' and ADDON.getSetting('use_meta') == 'true':
            addon.add_directory({'mode': 'GETLINKS', 'url': str(urls), 'linkback': str(name),'title': yname},infoLabels, contextMenuItems, context_replace=True,img=str(img),fanart=infoLabels['backdrop_url'],total_items=totalitems)
            #setView('movies', 'movie-view')
            xbmc.executebuiltin("Container.SetViewMode(503)")
        else:    
            addon.add_directory({'mode': 'GETLINKS', 'url': str(urls), 'linkback': str(name)},{'title': yname}, contextMenuItems, context_replace=True,img=str(img),total_items=totalitems)
            setView(None, 'default-view')
    if 'Previous Entries</a>' in str(html):
        r = re.compile('<a href="(.+?)"(?=>&laquo; Prev)').findall(str(html))
        for np in r:
            addon.add_directory({'mode': 'GETI', 'url': np, 'linkback': linkback}, {'title': 'Next Page>>'},img = '')
    
def GETLINKS(url):
    html = GET_HTML(url)
    img = re.compile(r'<img class="alignnone".+?src="(.+?)" alt=').findall(str(html))
    for img in img:
        continue
    r = re.compile(r'"text-align: center;"><a href="(http://oneclickmoviez.com/dws/.+?)" target').findall(str(html))
    if len(r) ==0:
        r = re.compile(r'<p><a href="http://oneclickseriez.com/downloads/?(.+?)" target=').findall(str(html))
    
    sources = []
    for hoster in r:
        hoster = str(hoster).replace('?','')
        if 'CRAMIT' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Cramit')
                sources.append(hosted_media)
                
                
        if 'BAYFILES' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Bayfiles')
                sources.append(hosted_media)
                
        if 'CYBERLOCKER' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Cyberlocker')
                sources.append(hosted_media)
        if 'TURBOBIT' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Turbobit')
                sources.append(hosted_media)
        if 'UPLOADED' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Uploaded')
                sources.append(hosted_media)
        if 'PUTLOCKER' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Putlocker')
                sources.append(hosted_media)
        if 'EXTABIT' in hoster:
            html = GET_HTML(hoster)
            r = re.compile("Lbjs.TargetUrl = '(.+?)';").findall(str(html))
            for fileurl in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Extrabit')
                sources.append(hosted_media)
        if 'megashares' in hoster:
            html = GET_HTML(hoster)
            r = re.compile(r'var request_uri = "/index.php?(.+?)=(.+?)";').findall(str(html))
            for server, fileno in r:
                server = str(server).replace('?','')
                fileurl = 'http://'+server+'.megashares.com/index.php?'+server+'='+fileno
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Megashares')
                sources.append(hosted_media)
        if '2SHARED' in hoster:
            html = GET_HTML(hoster)
            r = re.compile('">(.+?)</div>').findall(str(html))
            for fileno in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='2shared')
                sources.append(hosted_media)
        if 'HOTFILE' in hoster:
            html = GET_HTML(hoster)
            r = re.compile('">(.+?)</div>').findall(str(html))
            for fileno in r:
                hosted_media = urlresolver.HostedMediaFile(url=fileurl, title='Hotfile')
                sources.append(hosted_media)
    source = urlresolver.choose_source(sources)
    if source: stream_url = source.resolve()
    else: stream_url = ''
    liz=xbmcgui.ListItem(linkback, iconImage='',thumbnailImage=img)
    liz.setInfo('Video', {'Title': linkback} )
    liz.setProperty("IsPlayable","true")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=stream_url,isFolder=False,listitem=liz)#; Addon.resolve_url(stream_url)
    xbmc.Player().play(stream_url,liz)
    GA("NONE","Watching")

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
        print '+++++++'+xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':
        print '+++++++++'+addon.get_setting(viewType)
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType))

            
def FIND_IMDB(url):
    html = GET_HTML(url)
    r = re.compile(r'<a href="(http://oneclickmoviez.com/dws/IMDB/.+?)" target=',re.I).findall(str(html))
    for url in r:
        html = GET_HTML(url)
        r = re.compile(r"Lbjs.TargetUrl = 'http://www.imdb.com/title/(.+?)/'",re.I).findall(str(html))
        for imdb in r:
            return imdb

def GET_META(name,year,types):
    type = types
    if type == 'None':
        infoLabels = {'cover_url': '','title': name }
    if type == 'movie':
        meta = grab.get_meta(types,name,None,None,'',overlay=6)
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],
                      'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url']}
        if infoLabels['cover_url'] == '' : infoLabels['cover_url'] = "%s/resources/art/TVRNoimage.png"%(ADDON.getAddonInfo("path"))

    return infoLabels
                                                                                            

def GET_HTML(url):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        html = BeautifulSoup(link)
        return html
    except Exception, e:
        print "Failed to retrieve page: %s" %url
        print "Urllib2 error: "+str(e)
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Connection Error[/B][/COLOR],Error connecting to OneClickMoviez,10000,%s/resources/art/warning.png)"%ADDON.getAddonInfo("path"))
        GA("None","HTML_ERROR: "+str(e))
        return main()

def SEARCH():
    print 'SEARCH'
    last_search = addon.load_data('search')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I]Search OneClickMoviez[/B][/I]')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')# sometimes you need to replace spaces with + or %20#
        addon.save_data('search',search_entered)
    if search_entered == None or len(search_entered)<1:
        MAIN()
    else:
        url = 'http://oneclickmoviez.com/?s="%s"'%(search_entered)
        types = None
        GETINDEX(url,linkback,types)
        GA("None","SEARCH: ")

def CLEAN_NAME(name):
    name = name.replace ('-',' ')
    name = name.replace('_',' ')
    name = name.replace('.',' ')
    return name

def HELP():
    help = SHOWHELP()
    help.doModal()
    del help

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
        
    if addon.get_setting('auto_view') == 'True':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType) )


class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,"%s/resources/art/Help.png"%ADDON.getAddonInfo("path")))
    def onAction(self, action):
        if action == 92 or action == 10:
            self.close()


def main():
    addon.add_directory({'mode': 'LATEST', 'linkback': '','types': 'movie'}, {'title': 'Latest'}, img = '')
    addon.add_directory({'mode': 'BluRay', 'linkback': '','types': 'movie'}, {'title': 'BluRay'}, img = '')
    addon.add_directory({'mode': 'BR_BDRIP', 'linkback': '','types': 'movie'}, {'title': 'BRRIP/BDRIP'}, img = '')
    addon.add_directory({'mode': 'DVDR', 'linkback': '','types': 'movie'}, {'title': 'DVDR'}, img = '')
    addon.add_directory({'mode': 'DVDRIP', 'linkback': '','types': 'movie'}, {'title': 'DVDRIP'}, img = '')
    addon.add_directory({'mode': 'DVDSCR', 'linkback': '','types': 'movie'}, {'title': 'DVDSCR'}, img = '')
    addon.add_directory({'mode': 'R5', 'linkback': '','types': 'movie'}, {'title': 'R5'}, img = '')
    addon.add_directory({'mode': 'TV_PACKS', 'linkback': 'tv','types': 'None'}, {'title': 'TV Packs'}, img = '')
    addon.add_directory({'mode': 'Uncategorized', 'linkback': '','types': 'None'}, {'title': 'Uncategorized'}, img = '')
    addon.add_directory({'mode': 'Search', 'linkback': '','types': 'None'},{'title': 'Search'}, img = '')
    addon.add_directory({'mode': 'ResolverSettings', 'linkback': '','types': 'None'}, {'title': '[COLOR green]Resolver Settings[/COLOR]'}, img = '')
    addon.add_directory({'mode': 'NEEDHELP', 'linkback': '','types': 'None'}, {'title': '[B][COLOR blue]Having problems, Need help, Click here[/B][/COLOR]'}, img = '')
    GA("None","MAIN")
    setView(None, 'default-view')

if mode == 'main':
    main()

elif mode == 'LATEST':
    url = BASE_URL
    GA("None",mode)
    GETINDEX(url,linkback,types)

elif mode == 'BluRay':
    GA("None",mode)
    url = BASE_URL+'category/bluray/'
    GETINDEX(url,linkback,types)

elif mode == 'BR_BDRIP':
    GA("None",mode)
    url = BASE_URL+'category/brripbdrip/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDR':
    GA("None",mode)
    url = BASE_URL+'category/dvdr/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDRIP':
    GA("None",mode)
    url = BASE_URL+'category/dvdrip/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDSCR':
    GA("None",mode)
    url = BASE_URL+'category/dvdscr/'
    GETINDEX(url,linkback,types)

elif mode == 'R5':
    GA("None",mode)
    url = BASE_URL+'category/r5/'
    GETINDEX(url,linkback,types)

elif mode == 'TV_PACKS':
    GA("None",mode)
    url = BASE_URL+'category/tv-packs/'
    GETINDEX(url,linkback,types)

elif mode == 'Uncategorized':
    GA("None",mode)
    url = BASE_URL+'category/uncategorized/'
    GETINDEX(url,linkback,types)

elif mode == 'GETI':
    GA("None",mode)
    GETINDEX(url,linkback,types)

elif mode == 'GETLINKS':
    GA("None",mode)
    GETLINKS(url)

elif mode == 'Search':
    GA("None","Search")
    SEARCH()

elif mode == 'ResolverSettings':
    urlresolver.display_settings()
    main()

elif mode == 'NEEDHELP':
    GA("None",mode)
    HELP()

addon.end_of_directory()
