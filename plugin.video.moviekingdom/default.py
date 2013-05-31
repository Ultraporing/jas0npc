import urllib,urllib2,re,cookielib,xbmcplugin,xbmcgui,xbmcaddon,socket,os,shutil,urlresolver,string,xbmc
import HTMLParser,base64,datetime,time,json
local = xbmcaddon.Addon(id='plugin.video.moviekingdom')
sys.path.append( os.path.join( local.getAddonInfo('path'), 'resources', 'lib' )) 

from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from BeautifulSoup import BeautifulSoup
from metahandler import metahandlers
from sqlite3 import dbapi2 as database
from xgoogle.search import GoogleSearch, SearchError
from hashlib import md5
from ga import *

socket.setdefaulttimeout(300)# Bloody tvdb - slow or dead
grab = metahandlers.MetaData(preparezip = False)
net = Net()
IMDM = None
Addon = Addon('plugin.video.moviekingdom', sys.argv)
BASE_URL = 'http://www.movie-kingdom.com/'
announce = 'http://jas0npc-xbmc-repository.googlecode.com/svn/trunk/announce/MK_NOTICE.xml'
cookie_path = os.path.join(Addon.get_profile(), 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
downloadPath = local.getSetting('download-folder')

if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)
    
art = xbmc.translatePath(os.path.join(local.getAddonInfo('path'), 'resources', 'art'))
error_pic = os.path.join(art, 'redx.png')
                         

user = local.getSetting('username')
passs = local.getSetting('password')
password = md5(passs).hexdigest()
print 'moviekingdom v1.0'


def MAIN():
    try:
        link = net.http_GET(announce).content
        ANNOUNCEMENT(link)
    except urllib2.URLError, e:
        pass
    #addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage)
    addDir(30,None,BASE_URL,None,None,None,'TV Menu',os.path.join(art, 'tvmenu.png'),0,'')
    addDir(40,None,BASE_URL,None,None,None,'Movie Menu',os.path.join(art, 'moviemenu.png'),0,'')
    addDir(60,None,BASE_URL,None,None,None,'[COLOR green][B]Search Menu[/B][/COLOR]',os.path.join(art, 'searchman.jpg'),0,'')
    addSpecial('[COLOR yellow]Resolver Settings[/COLOR]','www.nonsense.com','10','')
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','20','')
    GA("None","MAIN")
    setView('movies', 'default')
    
def TV_SECTION(url):
    addDir(34,'newest_episodes',BASE_URL+'new-shows',None,None,None,'New Episodes',os.path.join(art, 'ntvepisodes.png'),0,'')
    addDir(31,'tv_genres',BASE_URL,None,None,None,'Shows By Genre','',0,'')
    addDir(32,'featured',BASE_URL,None,None,None,'Featured Shows',os.path.join(art, 'featuredshows.png'),0,'')
    addDir(33,'random_tv',BASE_URL,None,None,None,'Random Shows','',0,'')
    setView('movies', 'default')
    GA("None","TV Section")

def TV_GENRES(url):
    html = GET_HTML(url)
    if html == None:
        return
    r = re.findall(r'TV shows</a>\n<ul class="sub-menu">(.+?)</ul>\n</li>',html,re.M|re.DOTALL)
    pattern = 'a href="(http://www.movie-kingdom.com/tv-tags/.+?)">(.+?)</a></li>'
    r = re.findall(pattern,str(r))
    totalItems = len(r)
    for url, name in r:
        addDir(50,mode2,url,None,None,None,name,'',totalItems,'')
    setView('movies', 'anything')
    GA("None","TV Genres")

def FEATURED_SHOWS(url):
    html = GET_HTML(url)
    if html == None:
        return
    r = re.findall(r'<div id="featured">(.+?)<div id="featured">',html,re.M|re.DOTALL)
    pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>.+?</h2>'
    r = re.findall(pattern,str(r),re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        name = name.replace('\\','')
        addDir(50,'season',url,'tvshow',None,None,name,'',totalItems,'')
    setView('movies', 'anything')
    GA("None","Featured Shows")

def RANDOM_SHOWS(url):
    html = GET_HTML(url)
    if html == None:
        return
    r = re.findall('<h3 class="title">Random TV Shows</h3>(.+?)class="widget tabbertabs">',html,re.M|re.DOTALL)
    pattern = ' class="imageWrapper">.+?<a href="(.+?)" class=".+?<p.+?">(.+?)</p>'
    r = re.findall(pattern,str(r),re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        name = name.replace('\\n','').replace('\\','')
        addDir(50,'season',url,'tvshow',None,None,name,'',totalItems,'')
    setView('movies', 'anything')
    GA("None","Random Shows")

def NEWEST_EPISODES(url):
    html = GET_HTML(url)
    if html == None:
        return
    pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>.+?</h2>'
    r = re.findall(pattern,html,re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        name = name.replace('\\','')
        print '+++++++++++++++++NAMES: '+str(name)
        addDir(50,mode2,url,'tvshow',None,None,name,'',totalItems,'False')
    setView('movies', 'anything')
    GA("None","Newest Episodes")

def MOVIE_SECTION(url):
    #addDir(mode,None,BASE_URL+'new-movies',None,None,None,'New Movies','')
    addDir(41,'movie_genres',BASE_URL,None,None,None,'Movies By Genre','',0,'')
    addDir(42,'random_movies',BASE_URL,None,None,None,'Random Movies','',0,'')
    addDir(43,'latest_movies_added',BASE_URL,None,None,None,'Latest Movies Added',os.path.join(art, 'latestmovies .png'),0,'')
    setView('movies', 'default')
    GA("None","Movie Section")

def MOVIES_GENRES(url):
    html = GET_HTML(url)
    if html == None:
        return
    r = re.findall(r'Movies</a>\n<ul class="sub-menu">(.+?)</ul>\n</li>',html,re.M|re.DOTALL)
    pattern = 'a href="(http://www.movie-kingdom.com/movie-tags/.+?)">(.+?)</a></li>'
    r = re.findall(pattern,str(r))
    totalItems = len(r)
    for url, name in r:
        addDir(50,mode2,url,None,None,None,name,'',totalItems,'')
    setView('movies', 'anything')
    GA("None","Movie Genres")

def RANDOM_MOVIES(url):
    html = GET_HTML(url)
    if html == None:
        return
    #temp = re.findall(r'Released: <a href="http://www.movie-kingdom.com/index.php\?menu=search\&year=.+?">(.+?)</a>.+?IMDB rating:.+?<a href="http://www.imdb.com/title/(.+?)" tar',html,re.M|re.DOTALL)
    #for year, IMDM in temp:
    #    IMDM = IMDM+':'+year
    r = re.findall('<h3 class="title">Random Movies</h3>(.+?)<div class="widget">.+?<h3 class="title">Random TV Shows',html,re.M|re.DOTALL)
    pattern = ' class="imageWrapper">.+?<a href="(.+?)" class=".+?<p.+?">(.+?)</p>'
    r = re.findall(pattern,str(r),re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        name = name.replace('\\n','').replace('\\','')
        addDir(50,'random_movies',url,'movie',None,None,name,'',totalItems,'False')
    setView('movies', 'anything')
    GA("None","Random Movies")

def LATEST_MOVIES_ADDED(url):
    html = GET_HTML(url)
    if html == None:
        return
    
    r = re.findall(r'<h3>Latest Movies Added</h3>(.+?)<div id="tv_guide">',html,re.M|re.DOTALL)
    #pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>'
    pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>'#.+?Released:'
    #pattern +=' <a href=".+?">(.+?)</a>.+?IMDB rating:.+?<a '
    #pattern +='href="http://www.imdb.com/title/(.+?)" tar'
    r = re.findall(pattern,str(r),re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:#, year, IMDM in r:
        name = name.replace('\\','')
        #IMDM = IMDM+':'+year
        addDir(50,mode2,url,'movie',None,None,name,'',totalItems,'False')
    setView('movies', 'anything')
    GA("None","Latest Movies")

def INDEX(url,name,types):
    sources = []
    html = GET_HTML(url)
    if html == None:
        return
    if mode2 == 'movie_genres':
        pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a'#Released:'
        #pattern +=' <a href=".+?">(.+?)</a>.+?IMDB rating:.+?<a '
        #pattern +='href="http://www.imdb.com/title/(.+?)" tar'
        r = re.findall(pattern,html,re.M|re.DOTALL)
        totalItems = len(r)
        for url, name in r:#, year, IMDM in r:
            name = name.replace('\\','')
            #IMDM = IMDM+':'+year
            addDir(50,'random_movies',url,'movie',None,'',name,'',totalItems,'False')
            setView('movies', 'anything')
    elif mode2 == 'tv_genres':
        pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>.+?IMDB rating:.+?<a href='
        pattern +='"http://www.imdb.com/title/(.+?)" targ'
        r = re.findall(pattern,html,re.M|re.DOTALL)
        totalItems = len(r)
        for url, name, IMDM in r:
            name = name.replace('\\','')
            addDir(50,'season',url,'tvshow',IMDM,None,name,'',totalItems,'')
        setView('movies', 'anything')
    elif mode2 == 'season':
        pattern = 'class="page-numbers current" href="(.+?)">(.+?)</a>'
        IMDM = re.findall(r'IMDB rating:.+?<a href="http://www.imdb.com/title/(.+?)" tar',html,re.M|re.DOTALL)
        r = re.findall(pattern, html, re.M|re.DOTALL)
        totalItems = len(r)
        for url, season in r:
            name = re.split('show',url)
            name = str(name[1]).replace('/',' ').replace('-',' ')
            addDir(50,'episode',url,'season',IMDM[0],None,name,'',totalItems,'')
        setView('movies', 'season')
    elif mode2 == 'episode':
        r = re.findall(r'class="icon-eye-open"></i>(.+?)</h2>',html,re.M|re.DOTALL)
        pattern = 'a href="(.+?)" title=".+?">(.+?)</a>'
        r = re.findall(pattern,str(r),re.M|re.DOTALL)
        totalItems = len(r)
        for url, episode in r:
            addDir(50,'newest_episodes',url,'episode',linkback,meta_name,episode,'',totalItems,'False')
        setView('movies', 'anything')
    elif mode2 == 'latest_movies_added'or mode2 == 'random_movies' or mode2 == 'newest_episodes':
        if types == 'episode' or types == 'tvshow':
            title2 = name
            title = name
            temp = re.split('show/',url)
            title2 = str(temp[1]).replace('/','-')
            title = re.split('season',title2)
            title = str(title[0]).replace('-',' ').strip()
        if types == 'movie':
            title = name
            title2 = name
        pattern = '<strong>(.+?)</strong>.+?<a href="(.+?)" tar'
        r = re.findall(pattern,html,re.I|re.M|re.DOTALL)
        for name, url in r:
            url = url+':'
            r = re.findall('http://adf.ly/.+?\/(.+?):',url)
            for url in r:
                url = 'http://'+url
            r = re.findall('//(.+?)/',url)
            for name in r:
                if '.' in name:
                    name = name.rpartition('.')
                    name = str(name[0])
            name = name.replace('www.','')
            media = urlresolver.HostedMediaFile(url=url, title=name)
            sources.append(media)
    source = urlresolver.choose_source(sources)
    try:
        if source:
            stream_url = source.resolve()
            if types == 'episode':
                types ='tvshow'
            title2 = title2.replace('-',' ')
            infoLabels = GRABMETA(title,types,linkback)
            liz=xbmcgui.ListItem(title2, iconImage='',thumbnailImage=infoLabels['cover_url'])
            liz.setInfo('Video', {'Title': title2} )
            liz.setProperty("IsPlayable","true")
            GA("None","Watching: '"+str(title2))
            xbmc.Player().play(stream_url, liz)
        else:
            stream_url = ''
            return
    except:
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Streaming Error[/B][/COLOR],Try Another Hoster,5000,"+error_pic+")")
        return
def SEARCHMENU():
    #addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage,totalItems,folder)
    addDir(90,'searchbyword',BASE_URL,None,None,None,'Search By Word','',0,'')
    addDir(91,'searchbyyear',BASE_URL,None,None,None,'Search By Year','',0,'')
    addDir(92,'searchbydirector',BASE_URL,None,None,None,'Search By Director','',0,'')
        
def SEARCHBYWORD():
    last_search = Addon.load_data('search')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I] SEARCH Movie-kingdom[/B][/I]')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')# sometimes you need to replace spaces with + or %20#
        Addon.save_data('search',search_entered)
    if search_entered == None or len(search_entered)<1:
        SEARCHMENU()
    else:
        url = 'http://www.movie-kingdom.com/index.php?menu=search&query=%s'%(search_entered)
        html = GET_HTML(url)
        if html == None:
            return
        net.save_cookies(cookie_jar)
        pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>.+?</h2>'
        IMDM = re.findall(r'IMDB rating:.+?<a href="http://www.imdb.com/title/(.+?)" tar',html,re.M|re.DOTALL)
        r = re.findall(pattern,html,re.M|re.DOTALL)
        totalItems = len(r)
        for url, name in r:
            if '/show/' in url:
                mode2 = 'newest_episodes'
                types = 'tvshow'
                linkback = None
                video = ''
            else:
                mode2 = 'random_movies'
                types = 'movie'
                linkback = IMDM[0]
                video = 'False'
            addDir(50,mode2,url,types,None,'',name,'',totalItems,'False')
        GA("None","Search: "+search_entered)
    setView('movies', 'anything')

def SEARCHBYYEAR():
    keyboard = xbmcgui.Dialog().numeric(0, '[B][I] SEARCH Movie-kingdom[/B][/I]')
    if len(keyboard) != 4:
        dialog = xbmcgui.Dialog()
        dialog.ok("[B]SEARCH ERROR[/B]", "Search by year date MUST be four numbers long.","eg. 1998, 2011, 2013 only.","")
        SEARCHMENU()
    url = 'http://www.movie-kingdom.com/index.php?menu=search&year=%s' %(keyboard)
    html = GET_HTML(url)
    if html == None:
        return
    pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>'
    r = re.findall(pattern,html,re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        if 'com/show/' in url:
            types = 'tvshow'
            mode2 = 'season'
            video = ''
    
        if 'com/movie/' in url:
            types = 'movie'
            mode2 = 'latest_movies_added'
            video = 'False'
            #addDir(50,mode2,url,types,linkback,'',name,'',totalItems,'False')
        addDir(50,mode2,url,types,None,None,name,'',totalItems,video)
    setView('movies', 'anything')
    
def SEARCHBYDIRECTOR():
    last_search = Addon.load_data('director')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I] SEARCH Movie-kingdom by Director[/B][/I]')
    last_search = last_search.replace('%20',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','%20')# sometimes you need to replace spaces with + or %20#
        Addon.save_data('director',search_entered)
    if search_entered == None or len(search_entered)<1:
        SEARCHMENU()
    url = 'http://www.movie-kingdom.com/index.php?menu=search&director=%s'%(search_entered)
    html = GET_HTML(url)
    if html == None:
        return
    pattern = '<h2>.+?<a href="(.+?)" title=".+?">(.+?)</a>'
    r = re.findall(pattern,html,re.M|re.DOTALL)
    totalItems = len(r)
    for url, name in r:
        if 'com/movie/' in url:
            types = 'movie'
            mode2 = 'latest_movies_added'
        else:
            types = 'tvshow'
            mode2 = 'season'
        addDir(50,mode2,url,types,None,None,name,'',totalItems,'False')
    GA("None","SEARCH BY DIRECTOR: "+search_entered)
    setView('movies', 'anything')
    
def TRAILERSEARCH(url, name, manual=False):#Thanks to Eldorado for coding this in icefilms
    search = name
    res_name = []
    res_url = []
    imdb_id = linkback
    site = ' site:http://www.youtube.com '
    results = SearchGoogle(search+' official trailer', site)
    for res in results:
        if res.url.encode('utf8').startswith('http://www.youtube.com/watch'):
            res_name.append(res.title.encode('utf8'))
            res_url.append(res.url.encode('utf8'))
    results = SearchGoogle(search[:(len(search)-7)]+' official trailer', site)
    for res in results:
        if res.url.encode('utf8').startswith('http://www.youtube.com/watch') and res.url.encode('utf8') not in res_url:
            res_name.append(res.title.encode('utf8'))
            res_url.append(res.url.encode('utf8'))
            
    dialog = xbmcgui.Dialog()
    ret = dialog.select(search + ' trailer search',res_name)
    trailer_url = res_url[ret - 0]
    GA("None","Watching Trailer: "+name)
    try:
        xbmc.executebuiltin(
            "PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid=%s&quality=720p)" 
            % str(trailer_url)[str(trailer_url).rfind("v=")+2:] )

        grab.update_trailer('movie', imdb_id, trailer_url)
        xbmc.executebuiltin("XBMC.Container.Refresh")
        GA("None","Watching Trailer: "+name)
    except:
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Error[/B][/COLOR],Please try again,10000,error_pic)")
        GA("None","ERROR Watching Trailer")
        return

    
def SearchGoogle(search, site):
    gs = GoogleSearch(''+search+' '+site)
    gs.results_per_page = 25
    gs.page = 0
    try:
        results = gs.get_results()
    except Exception, e:
        print '***** Error: %s' % e
        return None
    return results

        
def GET_HTML(url):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        html = link
        return html
    except urllib2.URLError, e:
        print "Failed to retrieve page: %s" %url
        print 'Urllib2 error: '+str(e)
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Connection Error[/B][/COLOR],Network Error,5000,"+error_pic+")")
        GA("HTML ERROR: ",str(e))        
        return MAIN()

    
def ANNOUNCEMENT(link):
    #GA("ANNOUNCEMENT","Site Down")
    r = re.findall(r'<title>(.+?)<Etitle><line1>(.+?)<Eline1><line2>(.+?)<Eline2><line3>(.+?)<Eline3>',link,re.I)
    for title, line1, line2, line3 in r:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('[B][COLOR red]'+title+'[/B][/COLOR]','[COLOR red]'+line1+'[/COLOR]','[COLOR red]'+line2+'[/COLOR]','[COLOR red]'+line3+'[/COLOR]')
    return
    
    
def HELP():
    help = SHOWHELP()
    help.doModal()
    GA("None","NEED HELP")
    del help

def setView(content, viewType):
        # set content type so library shows more views and info
        if content:
                xbmcplugin.setContent(int(sys.argv[1]), content)
        if ADDON.getSetting('auto-view') == 'true':#<<<----see here if auto-view is enabled(true) 
                xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )#<<<-----then get the view type

class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,os.path.join(art,'Help.png')))
    def onAction(self, action):
        if action == 92 or action == 10:
            self.close()

def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
        return param

def VIDEOLINKS(url):
    print 'VIDEOLINKS URL: '+str(url)

def GRABMETA(name,types,linkback):
    type = types
    if type == None: infoLabels = {'cover_url': '','title': name}
    if type == 'tvshow':
        if '-' in name:
            name = re.split('-',name)
            name = str(name[0]).strip()
        else:
            name = name
        meta = grab.get_meta('tvshow',name,None,None,None,overlay=6)

        infoLabels = {'backdrop_url': meta['backdrop_url'], 'cover_url': meta['cover_url'],
                      'plot': meta['plot'], 'title': name, 'trailer_url': meta['trailer_url']}
    if type == 'movie':
        meta = grab.get_meta('movie',name,None,None,None,overlay=6)

        infoLabels = {'backdrop_url': meta['backdrop_url'], 'cover_url': meta['cover_url'],
                      'plot': meta['plot'], 'title': name, 'rating': meta['rating'],
                      'plot': meta['plot'], 'trailer_url': meta['trailer_url'], 'premiered': meta['premiered']}
    if type == 'season':
        temp = re.split('season',name,re.I)
        name = str(temp[0]).strip()
        season = str(temp[1]).strip()
        meta = grab.get_seasons(name,'',season)
        r = re.findall(r"'cover_url': '(.+?)'",str(meta))
        for thumb in r:
            infoLabels ={'cover_url': thumb, 'title': name}
    if type == 'episode':
        name = name+':'
        r = re.findall('Season\s(.+?). Episode (.+?):',name)
        for season, episode in r:
            meta = grab.get_episode_meta('',linkback,int(season),int(episode),episode_title='', overlay=6)
            infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                          'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'studio': meta['studio'],
                          'backdrop_url': meta['backdrop_url']}
    return infoLabels

def addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage,totalItems,video):
    img = iconimage
    u=sys.argv[0]+"?mode="+str(mode)+"&mode2="+str(mode2)+"&url="+str(url)+"&types="+str(types)+"&linkback="+str(linkback)+"&meta_name="+str(meta_name)+"&name="+str(meta_name)+"&name="+str(name)+"&iconimage="+str(iconimage)+"&totalItems="+str(totalItems)+"&video="+str(video)
    if local.getSetting("enable_meta") == "true" :
        infoLabels = GRABMETA(name,types,linkback)
        if types == 'movie' and meta_name != 'videolinks' and linkback != None:
            try:
                print 'adddir linkback: '+str(linkback)
                year = re.split(':',linkback)
                year = year[1]
                name = str(name)+':[COLOR yellow] Released: '+year+' IMBD Rating: '+str(infoLabels['rating'])+' [/COLOR]'
            except:
                pass


        if types == 'movie' and meta_name != 'videolinks' and linkback == None:
            year = re.split('-',str(infoLabels['premiered']))
            year = year[0]
            name = str(name)+':[COLOR yellow] Released: '+year+' IMBD Rating: '+str(infoLabels['rating'])+' [/COLOR]'

    else:
        infoLabels = {'cover_url': '', 'title': name}
    if types == None: img = iconimage
    else: img = infoLabels['cover_url']
    ok = True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=img)
    if types == 'movie':# and types != None: 
        liz.addContextMenuItems([('Search for trailer', "XBMC.RunPlugin(%s?mode=%s&name=%s&url=%s&linkback=%s&types=%s)"
                                  %(sys.argv[0],200,infoLabels['title'],url,linkback,types))])
    try:
        if types != None: liz.setProperty('fanart_image', infoLabels['backdrop_url'])
    except:
        pass
    liz.setInfo( type="Video", infoLabels=infoLabels)
    if 'False' in video:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False,totalItems=int(totalItems))
        
    else:
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=int(totalItems))
    return ok

def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    liz.setProperty('fanart_image', os.path.join(art,'xbmcback.png'))
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?url=%s&mode=%s&name=%s"%(url,mode,name),isFolder=False,listitem=liz)


params=get_params()
mode=None
mode2=None
url=None
types=None
linkback=None
meta_name=None
name=None
totalItems=None
video=None
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:
        meta_name=urllib.unquote_plus(params["meta_name"])
except:
        pass

try:
        linkback=urllib.unquote_plus(params["linkback"])
except:
        pass
try:
        types=urllib.unquote_plus(params["types"])
except:
        pass
try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
        mode2=urllib.unquote_plus(params["mode2"])
except:
        pass
try:
        totalItems=int(params["totalItems"])
except:
        pass
print '----------------------------------------------------'
print 'Mode: '+str(mode)
print 'Mode2: '+str(mode2)
print 'URL: '+str(url)
print 'TYPEs: '+str(types)
print 'Linkback: '+str(linkback)
print 'Meta_Name: '+str(meta_name)
print 'Name: '+str(name)
print 'TotalItems: '+str(totalItems)
print '----------------------------------------------------'

if mode==None or url==None or len(url)<1:
    MAIN()

elif mode == 10:
    urlresolver.display_settings()
elif mode == 20:
    HELP()
elif mode == 30:
    TV_SECTION(url)
elif mode == 31:
    TV_GENRES(url)
elif mode == 32:
    FEATURED_SHOWS(url)
elif mode == 33:
    RANDOM_SHOWS(url)
elif mode == 34:
    NEWEST_EPISODES(url)
elif mode == 40:
    MOVIE_SECTION(url)
elif mode == 41:
    MOVIES_GENRES(url)
elif mode == 42:
    RANDOM_MOVIES(url)
elif mode == 43:
    LATEST_MOVIES_ADDED(url)
elif mode == 50:
    INDEX(url,name,types)
elif mode == 60:
    SEARCHMENU()
elif mode == 90:
    SEARCHBYWORD()
elif mode == 91:
    SEARCHBYYEAR()
elif mode == 92:
    SEARCHBYDIRECTOR()
elif mode == 100:
    VIDEOLINKS(url)
elif mode == 200:
    TRAILERSEARCH(url, name, meta_name)
    
    
xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=True)
