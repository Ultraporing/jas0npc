import urllib,urllib2,sys,re,xbmcplugin
import xbmcgui,xbmcaddon,xbmc
import time,os,urlresolver

local = xbmcaddon.Addon(id='plugin.video.AWEsomeDL')#
sys.path.append( "%s/resources/"%local.getAddonInfo('path') )
from metahandler import metahandlers
from BeautifulSoup import BeautifulSoup
from sqlite3 import dbapi2 as database
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon


addon = Addon('plugin.video.AWEsomeDL', sys.argv)#
datapath = addon.get_profile()
grab = metahandlers.MetaData()
linkback = None
net = Net()
art = xbmc.translatePath(os.path.join(local.getAddonInfo('path'), 'resources', 'art'))
announce = 'http://github.com/jas0npc/jas0npc/raw/master/announce/AWE_NOTICE.xml'
cookie_path = os.path.join(datapath, 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)
    
BASE_URL = 'http://www.awesomedl.com/'#
print 'AWEsomeDL v2.0.4'

def MAIN():#addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage)
    addDir(100,'latest',BASE_URL,None,'','','Latest Shows','')
    addDir(400,'search',BASE_URL,None,'','','Search','')
    addDir(410,'Popular',BASE_URL,None,'','','Popular Shows','')
    addDir(420,'newseries',BASE_URL,None,'','','New Series/Shows','')
    addSpecial('[COLOR yellow]Resolver Settings[/COLOR]','www.nonsense.com','60','')
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','50','')
    
    setView('movies', 'default')
    
def INDEX(url,linkback):
    print 'INDEX START URL: '+str(url)
    url = url.replace(' ','%20')
    html = GET_HTML(url,linkback)
    if html == None:
        return MAIN()
    html = html.encode('ascii','ignore')
    if mode2 == 'latest' or mode2 == 'search':
        r = re.findall(r'<div id="main"(.+?)<div class="navigation clearfix"',html,re.M|re.DOTALL)
        pattern = 'h2 class="title"><a href="(.+?)/" title.+?img'
    elif mode2 == 'Popular':
        r = re.findall(r'<h2 class="generic">Tag Archives:(.+?)<div class="navigation clearfix">',html,re.M|re.DOTALL)
        pattern = 'class="title"><a href="(.+?)/" title="Perma'
    elif mode2 == 'newseries':
        r = re.findall(r'class="post-wrap">(.+?)rel="bookmark">Read More</a>',html,re.M|re.DOTALL)
        pattern = '<h2 class="title"><a href="(.+?)/" ti'
    r = re.findall(pattern,str(r),re.DOTALL)
    for url in r:
        name = GET_NAME(url)
        addDir(500,mode2,url,'tvshow','',name,name,'')
    if "an> Older posts</a></d" in html and mode2 != 'Popular':
        r = re.findall(r'eft"><a href="(.+?)"(?= ><span>&laquo)',html)
        r = str(r[0]).replace('%5C','')
        addDir(None,'','',None,url,'','[B][COLOR green] <<<MENU[/COLOR][/B]','')
        addDir(100,mode2,r,None,url,'','[B][COLOR yellow]Next Page>>>[/B][/COLOR]','')
        
    setView('movies', 'anything')

def POPULAR(url):#addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage)
    html = html = GET_HTML(url,'')
    if html == None:
        return MAIN()
    r = re.findall(r'h3 class="widgettitle">Popular</h3>(.+?)<ul class="widget-wrap"><li',html,re.M|re.DOTALL)
    pattern = '<a href="(.+?)/"'
    r = re.findall(pattern,str(r),re.M|re.DOTALL)
    for url in r:
        name = GET_NAME(url)
        addDir(100,mode2,url,'tvshow',None,None,name,'')
    setView('movies', 'anything')

def NEWSERIES(url):
    html = GET_HTML(url,'')
    if html == None:
        return MAIN()
    r = re.findall(r'class="widgettitle">New Series / Shows</h(.+?)class="widgettitle">FRIENDS</',html,re.M|re.DOTALL)
    pattern = 'href="(.+?)/">'
    r = re.findall(pattern,str(r))
    for url in r:
        name = GET_NAME(url)
        addDir(100,mode2,url,'tvshow',None,None,name,'')
    setView('movies', 'anything')
    
def VIDEO_LINKS(url,name,types):
    content = None
    show_name = name
    html = GET_HTML(url,'')
    r = re.findall(r"Watch Online:(.+?)<a href='http://www.affbu",html,re.DOTALL|re.M|re.I)
    r = str(r).replace('|',' ')
    r = re.findall(r'href="(.+?)">(.+?)</a>',str(r),re.DOTALL)
    if int(len(r)) <= 3:

        for url, hoster in r:
            print url
            name = '[B][COLOR green]'+hoster+': [/B][/COLOR]'+meta_name
            addDir(600,'videolinks',url,'',show_name,'',name,'')
            setView('movies', 'hoster')
    '''BIG THANKS TO BSTRDMKR FOR THE HELP WITH THIS SECTION, HE DID THIS IN SUCH A TIDY
        WAY, MY WAY WAS A LOT BIGGER AND NOT AS TIDY'''
    if (len(r) >= 6):
        post_pattern = r"<b><u>Watch Online:</b></u>(.+?)<a href='http://www.affbu"
        for post in re.finditer(post_pattern, html, re.DOTALL|re.M):
            content_pattern = r'\W?((?:[\w\.-])+)<br.+?href="(.+?)">(\w+)<.+?href="(.+?)">(\w+)<.+?href="(.+?)">(\w+)<'
            content = re.finditer(content_pattern, post.group(1), re.DOTALL)
        
        media = []
        for item in content:
            title, link1, host1, link2, host2, link3, host3 = item.groups()
            title = str(title.replace('.',' '))
            media.append((('[B][COLOR green]'+host1+'[/B][/COLOR]', title+'|'+link1), ('[B][COLOR green]'+host2+'[/B][/COLOR]', title+'|'+link2), ('[B][COLOR green]'+host3+'[/B][/COLOR]', title+'|'+link3)))
        for item in media:
            for info_set in item:
                name = "".join(str(info_set)).strip('[]')
                r = name.split('|')
                name = r[0].replace("('",'').replace("', '",' : ').replace("')","")
                url = r[1]
                r = name.split(':')
                show_name = str(r[1].strip())
                addDir(600,'videolinks',url,types,show_name,'',name,'')
    setView('movies', 'hoster')

    
def WATCH_MEDIA(url,types,linkback):
    url = url.replace("')","")
    if 'adf.ly' in url:
        try:
            url = url.replace("')","")
            html = GET_HTML(url,'')
            if html == None:
                return
            r = re.findall(r"var zzz = '(.+?)';\n.+?if\(ea",html,re.M)
            url = r[0]
        except Exception, e:
            print "Failed to retrieve page: %s" %url
            print 'Urllib2 error: '+str(e)
            return
    media_url = urlresolver.resolve(url)
    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()
    pl.add(str(media_url),)
    xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(pl)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=media_url,isFolder=False)
    
def GET_HTML(url,linkback):
    try:
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        link = link.decode("utf-8")
        link = link.encode("ascii","ignore")
        return link
    except urllib2.URLError, e:
        xbmc.executebuiltin("Notification([B][COLOR red]Connection Error[/B][/COLOR],"+str(e)+",5000,)")
        print 'URLLIB ERROR: '+str(e)
        return

def GET_NAME(url):
    name = str(url).rpartition('/')
    name = str(name[2]).replace('-',' ')
    return name
        

def SEARCH():
    last_search = addon.load_data('search')
    if not last_search: last_search = ''
    search_entered = ''
    keyboard = xbmc.Keyboard(search_entered, 'Search AwesomDL...XBMCHUB.COM')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText()#.replace(' ','+')# sometimes you need to replace spaces with + or %20#
        addon.save_data('search',search_entered)
    if search_entered == None or len(search_entered)<1:
        MENU()
    else:
        url = 'http://www.awesomedl.com/?s="%s"'%(search_entered).replace(' ','+')
        print url
        INDEX(url,'')


def HELP():
    help = SHOWHELP()
    help.doModal()
    del help


def GRABMETA(name,types):
    type = types
    if re.findall('season',name,re.I):
        name = str(name).split('season')
        name = str(name[0]).strip()
    elif re.findall('\ss[\d]{2}\s',name,re.I):
        name = re.split('\ss[\d]{2}\s',name)
        print 'Name--------'+str(name[0])+'------'
        name = name[0]
    print name
    meta = grab.get_meta('tvshow',name,None,None,None,overlay=6)
    infoLabels = {'backdrop_url': meta['backdrop_url'], 'cover_url': meta['cover_url'],
                  'plot': meta['plot'], 'title': name}
    if type == None: infoLabels = {'cover_url': '','title': name}
    
    return infoLabels


class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,os.path.join(art,'Help.png')))
    def onAction(self, action):
        if action == 92 or action == 10:
            xbmc.Player().stop()
            self.close()

def addDir(mode,mode2,url,types,linkback,meta_name,name,iconimage):
    img = iconimage
    u=sys.argv[0]+"?mode="+str(mode)+"&mode2="+str(mode2)+"&url="+str(url)+"&types="+str(types)+"&linkback="+str(linkback)+"&meta_name="+str(meta_name)+"&name="+str(meta_name)+"&name="+str(name)+"&iconimage="+str(iconimage)    
    if local.getSetting("enable_meta") == "true" :
        infoLabels = GRABMETA(name,types)
    else:
        infoLabels = {'cover_url': '', 'title': name}
    if types == None: img = iconimage
    else: img = infoLabels['cover_url']
    ok = True
    if mode2 == 'search': xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=img)
    try:
        if types != None: liz.setProperty('fanart_image', infoLabels['backdrop_url'])
    except:
        pass
    if local.getSetting("list_alphabetically") == "true" :
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE)
    if mode2 == 'latest' and local.getSetting("list_alphabetically") == "true":
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE)
    
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

    
def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?url=%s&mode=%s&name=%s"%(url,mode,name),isFolder=False,listitem=liz)

#below tells plugin about the views                
def setView(content, viewType):
        # set content type so library shows more views and info
        if content:
                xbmcplugin.setContent(int(sys.argv[1]), content)
        if ADDON.getSetting('auto-view') == 'true':#<<<----see here if auto-view is enabled(true) 
                xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )#<<<-----then get the view type

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

params=get_params()
mode=None
mode2=None
url=None
types=None
linkback=None
meta_name=None
name=None
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
print '----------------------------------------------------'
print 'Mode: '+str(mode)
print 'Mode2: '+str(mode2)
print 'URL: '+str(url)
print 'TYPEs: '+str(types)
print 'Linkback: '+str(linkback)
print 'Meta_Name: '+str(meta_name)
print 'Name: '+str(name)
print '----------------------------------------------------'
if mode==None or url==None or len(url)<1:
    MAIN()
elif mode == 50:
    HELP()
elif mode == 60:
    urlresolver.display_settings()
elif mode == 100:
    linkback = 'latest'
    INDEX(url,linkback)
elif mode == 200:
    linkback = 'top10'
    top10(url,linkback)
elif mode == 300:
    CATAGORY_VIEW(url)
elif mode == 400:
    SEARCH()
elif mode == 410:
    POPULAR(url)
elif mode == 420:
    NEWSERIES(url)
elif mode == 500:
    VIDEO_LINKS(url,name,types)
elif mode == 600:
    WATCH_MEDIA(url,types,linkback)

addon.end_of_directory()
