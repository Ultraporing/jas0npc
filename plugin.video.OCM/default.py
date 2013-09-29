import urllib,urllib2,sys,re,xbmcplugin,socket
import xbmcgui,xbmcaddon,xbmc,base64
import time,datetime,os,urlresolver
import cookielib,unicodedata,HTMLParser
ADDON = xbmcaddon.Addon(id='plugin.video.OCM')# Use this for setVIew
sys.path.append( "%s/resources/"%ADDON.getAddonInfo('path') )

from BeautifulSoup import BeautifulSoup
from htmlentitydefs import name2codepoint as n2cp
from metahandler import metahandlers
from sqlite3 import dbapi2 as database
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon

print 'OCM v 0.1.3'


addon = Addon('plugin.video.OCM', sys.argv)
announce = 'http://jas0npc-xbmc-repository.googlecode.com/svn/trunk/announce/OCM_NOTICE.xml'
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





def GETINDEX(url,linkback,types):
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    xbmc.executebuiltin("Container.SetViewMode(%s)"%addon.get_setting('view_modes'))
    html = GET_HTML(url)
    r = re.compile(r'<h2><a href="(.+?)".+?title=".+?">(.+?)</a>.+?src="(.+?)" alt=', re.DOTALL).findall(str(html))
    for urls, name, img in r:
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        name = str(name).decode("utf-8")
        name = name.encode("ascii","ignore")
        yname = name
        totalitems = len(name)
        name = re.findall(r'(.+?)(?=\s[0-9]{4}\s)',str(name))
        year = re.findall(r'.+?([0-9]{4}).+?',str(yname))
        year = ''.join(year).strip()
        name = ''.join(name).replace('-',' ').strip()
        print 'NAME IS: '+name
        print 'YEAR IS: '+year
        print 'YNAME IS: '+yname
        infoLabels = GET_META(name,year,types)
        contextMenuItems = []
        addon.add_directory({'mode': 'GETLINKS', 'url': str(urls), 'linkback': yname, 'types': 'None'}, {'title': str(yname)}, contextMenuItems, context_replace=True,img=str(img),fanart=infoLabels['backdrop_url'],total_items=totalitems)
            
    if 'Previous Entries</a>' in str(html):
        r = re.compile('<a href="(.+?)"(?=>&laquo; Prev)').findall(str(html))
        for np in r:
            addon.add_directory({'mode': 'GETI', 'url': np, 'linkback': linkback, 'types': types}, {'title': 'Next Page>>'},img = '')
    xbmc.executebuiltin("Container.SetViewMode(%s)"%addon.get_setting('view_modes'))
 
            
    
def GETLINKS(url,types,linkback):
    if linkback != 'None':
        print 'GETLINKS: '+linkback
        sources = []
    html = GET_HTML(url)
    img = re.compile(r'<img class="alignnone".+?src="(.+?)" alt=').findall(str(html))
    for img in img:
        continue
    r = re.compile(r'"text-align: center;"><a href="(http://oneclickmoviez.com/dws/.+?)" target').findall(str(html))
    if len(r) ==0:
        r = re.compile(r'<p><a href="http://oneclickseriez.com/downloads/?(.+?)" target=').findall(str(html))
    
    
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
    try:
        if source: stream_url = source.resolve()
        else: stream_url = ''
        liz=xbmcgui.ListItem(linkback, iconImage='',thumbnailImage=img)
        liz.setInfo('Video', {'Title': linkback} )
        liz.setProperty("IsPlayable","true")
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=stream_url,isFolder=False,listitem=liz)#; Addon.resolve_url(stream_url)
        xbmc.Player().play(stream_url,liz)
    except:
        xbmc.executebuiltin("XBMC.Notification([B]File Error[/B],File removed at hoster,10000,%s/resources/art/warning.png)"%ADDON.getAddonInfo("path"))
        print 'ERROR: '+linkback+' Not available at host: '+hoster
        return
        
    
            
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
                      'plot': meta['plot'],'writer': meta['writer'],'cover_url': meta['cover_url'],'title':['title'],
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
        search_entered = urllib.quote_plus(keyboard.getText())# == add + for spaces better than .replace(' ','+')# sometimes you need to replace spaces with + or %20#
        addon.save_data('search',search_entered)
    if search_entered == None or len(search_entered)<1:
        MAIN()
    else:
        url = 'http://oneclickmoviez.com/?s="%s"'%(search_entered)
        types = 'movie'
        GETINDEX(url,linkback,types)
        
def CLEAN_NAME(name):
    name = name.replace ('-',' ')
    name = name.replace('_',' ')
    name = name.replace('.',' ')
    return name

def main():
    addon.add_directory({'mode': 'LATEST', 'linkback': '','types': 'movie'}, {'title': 'Latest'}, img = '%s/resources/art/latest.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'BluRay', 'linkback': '','types': 'movie'}, {'title': 'BluRay'}, img = '%s/resources/art/bluray.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'BR_BDRIP', 'linkback': '','types': 'movie'}, {'title': 'BRRIP/BDRIP'}, img = '%s/resources/art/brrip.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'DVDR', 'linkback': '','types': 'movie'}, {'title': 'DVDR'}, img = '%s/resources/art/dvdr.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'DVDRIP', 'linkback': '','types': 'movie'}, {'title': 'DVDRIP'}, img = '%s/resources/art/dvdrip.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'DVDSCR', 'linkback': '','types': 'movie'}, {'title': 'DVDSCR'}, img = '%s/resources/art/dvdscr.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'R5', 'linkback': '','types': 'movie'}, {'title': 'R5'}, img = '%s/resources/art/r5.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'Uncategorized', 'linkback': '','types': 'movie'}, {'title': 'Uncategorized'}, img = '%s/resources/art/uncat.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'Search', 'linkback': '','types': 'None'},{'title': 'Search'}, img = '%s/resources/art/search.jpg'%ADDON.getAddonInfo("path"))
    addon.add_directory({'mode': 'ResolverSettings', 'linkback': '','types': 'None'}, {'title': '[COLOR green]Resolver Settings[/COLOR]'}, img = '%s/resources/art/settings.jpg'%ADDON.getAddonInfo("path"))
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','NEEDHELP',image ='%s/resources/art/help.jpg'%ADDON.getAddonInfo("path"))
    xbmc.executebuiltin("Container.SetViewMode(50)")
    
def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?url=%s&mode=%s&name=%s"%(url,mode,name),isFolder=False,listitem=liz)
    
def HELP():
    help = SHOWHELP()
    help.doModal()
    del help

def ANNOUNCEMENT(link):
    r = re.findall(r'<title>(.+?)<Etitle><line1>(.+?)<Eline1><line2>(.+?)<Eline2><line3>(.+?)<Eline3>',link,re.I)
    for title, line1, line2, line3 in r:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('[B][COLOR red]'+title+'[/B][/COLOR]','[COLOR red]'+line1+'[/COLOR]','[COLOR red]'+line2+'[/COLOR]','[COLOR red]'+line3+'[/COLOR]')
    return


class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,"%s/resources/art/Help.png"%ADDON.getAddonInfo("path")))
    def onAction(self, action):
        if action == 92 or action == 10:
            xbmc.Player().stop()
            self.close()


    
    

if mode == 'main':
    main()

elif mode == 'LATEST':
    url = BASE_URL
    GETINDEX(url,linkback,types)

elif mode == 'BluRay':
    url = BASE_URL+'category/bluray/'
    GETINDEX(url,linkback,types)

elif mode == 'BR_BDRIP':
    url = BASE_URL+'category/brripbdrip/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDR':
    url = BASE_URL+'category/dvdr/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDRIP':
    url = BASE_URL+'category/dvdrip/'
    GETINDEX(url,linkback,types)

elif mode == 'DVDSCR':
    url = BASE_URL+'category/dvdscr/'
    GETINDEX(url,linkback,types)

elif mode == 'R5':
    url = BASE_URL+'category/r5/'
    GETINDEX(url,linkback,types)

elif mode == 'TV_PACKS':
    url = BASE_URL+'category/tv-packs/'
    GETINDEX(url,linkback,types)

elif mode == 'Uncategorized':
    url = BASE_URL+'category/uncategorized/'
    GETINDEX(url,linkback,types)

elif mode == 'Adult':
    url = BASE_URL+'category/adult-18/'
    GETINDEX(url,linkback,types)

elif mode == 'GETI':
    GETINDEX(url,linkback,types)

elif mode == 'GETLINKS':
    GETLINKS(url,types,linkback)

elif mode == 'Search':
    SEARCH()

elif mode == 'ResolverSettings':
    urlresolver.display_settings()
    main()

elif mode == 'NEEDHELP':
    HELP()

addon.end_of_directory()
