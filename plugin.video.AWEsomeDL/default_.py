import urllib,urllib2,sys,re,xbmcplugin
import xbmcgui,xbmcaddon,xbmc
import time,os,urlresolver

local = xbmcaddon.Addon(id='plugin.video.AWEsomeDL')#
sys.path.append( "%s/resources/"%local.getAddonInfo('path') )
from metahandler import metahandlers
from sqlite3 import dbapi2 as database
from ga import GA
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon

addon = Addon('plugin.video.AWEsomeDL', sys.argv)#
datapath = addon.get_profile()
grab = metahandlers.MetaData()
linkback = None
net = Net()
cookie_path = os.path.join(datapath, 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)
    
BASE_URL = 'http://www.awesomedl.com/'#

def MAIN():
    addDir(100,BASE_URL,None,'','','Latest Shows','')
    addDir(200,BASE_URL,None,'','','Recommend Top 10 TV Shows','')
    addDir(300,BASE_URL,None,'','','Catagory View','')
    addDir(400,BASE_URL,None,'','','Search','')
    addSpecial('[COLOR yellow]Resolver Settings[/COLOR]','www.nonsense.com','60','')
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','50','')
    setView(None, 'default-view')
    GA("None","Main Menu")
    
def INDEX(url,linkback):
    url = url.replace(' ','%20')
    html = GET_HTML(url,linkback)
    html = html.decode("utf-8")
    html = html.encode("ascii","ignore")
    temp = url+':'
    r = re.findall(r"<h3 class='post-title entry-title'>\n<a href='(.+?)'>(.+?)</a>",html,flags = re.M|re.DOTALL)
    for url, name in r:
        addDir(500,url,'tvshow','',name,name,'')
    if "www.awesomedl.com/search?updated-max=" in html:
        r=re.compile(r"a class='blog-pager-older-link' href='(http://www.awesomedl.com/search\?updated-max=.+?)'").findall(html)
        addDir(100,r[0],None,url,'',' [B][COLOR yellow]Next Page>>>[/B][/COLOR]','')
    elif "older-link' title='Older Posts'>Older Posts</a>" in html:
        r = re.findall(r"href='(.+?)'(?= id='Blog1_blog-pager-older-link' title='Older Posts'>Older Posts</a>)",html)
        match = re.findall(r"label/(.+?)[:|?]",temp)
        match = match[0].replace('%20',' ')
        addDir(100,r[0],None,url,'','[B][COLOR yellow]'+match+': Next Page>>>[/B][/COLOR]','')
    elif "older-link' title='Next Posts'>Next Posts</a>" in html:
        r = re.findall(r"href='(.+?)'(?= id='Blog1_blog-pager-older-link' title='Next Posts'>Next Posts</a>)",html)
        addDir(100,r[0],None,url,'','[B][COLOR yellow]Next Page>>>[/B][/COLOR]','')
    GA("None","INDEX:")
    setView('tvshows', 'episode-view')

def CATAGORY_VIEW(url):
    html = GET_HTML(url,'')
    if html == None:
        return
    html = html.replace("/search/label/Site News",'').replace("/search/label/Other",'')
    r = re.findall(r"href='/(search/label/.+?)'>(.+?)</a></li",html)
    for catagory, name in r:
        addDir(100,BASE_URL+catagory,None,'','',name,'')
    GA("None","CATAGORY_VIEW: ")
    
        
def top10(url,linkback):
    html = GET_HTML(url,'')
    html = html.encode("ascii", "ignore")
    r = re.compile(r"<h2 class='title'>Recommend Top 10 TV Shows</h2>(.+?)</div><div class='widget Label'", re.DOTALL).findall(html)
    match = re.compile('a href="(.+?)">(.+?)</a>').findall(str(r))
    for url, name in match:
        name = name.replace(r"\'","'")
        addDir(100,url,'tvshow','latest','',name,'')
    GA("None","TOP10: ")
    setView('tvshows', 'tvshow-view')

def VIDEO_LINKS(url,name,types):
    show_name = name
    print show_name
    html = GET_HTML(url,'')
    r = re.findall(r"<b><u>Watch Online:</b></u>(.+?)<a href='http://www.affbu",html,re.DOTALL)
    r = re.findall(r'href="(.+?)">(.+?)</a>',r[0],re.DOTALL)
    GA(show_name,"VideoLINKS: "+str(len(r)))
    if (len(r)<=3):
        for url, hoster in r:
            name = '[B][COLOR green]'+hoster+'[/B][/COLOR]'
            addDir(600,url,types,show_name,show_name,name,'')
    """Big thanks to Bstrdmkr for the help with the below section, really nice
       way of doing this, You older devs are legends."""
    post_pattern = r"<b><u>Watch Online:</b></u>(.+?)<a href='http://www.affbu"
    for post in re.finditer(post_pattern, html, re.DOTALL|re.M):
        content_pattern = r'/>\W?((?:[\w\.-])+)<br.+?href="(.+?)">(\w+)<.+?href="(.+?)">(\w+)<.+?href="(.+?)">(\w+)<'
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
            addDir(600,url,types,show_name,show_name,name,'')

    
def WATCH_MEDIA(url,types,linkback):
    if 'adf.ly' in url:
        html = GET_HTML(url,'')
        r = re.findall(r"var zzz = '(.+?)';\n.+?if\(ea",html,re.M)
        url = r[0]
    r = linkback.split('Season')
    types = 'tvshow'
    infoLabels = GRABMETA(r[0],types)
    print str(infoLabels)
    media_url = urlresolver.resolve(url)
    liz=xbmcgui.ListItem(linkback, iconImage=infoLabels['cover_url'], thumbnailImage=infoLabels['cover_url'])
    liz.setInfo("Video", { "Title": linkback } )
    liz.setProperty("IsPlayable","true")
    #ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=media_url,isFolder=False,listitem=liz)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=media_url,isFolder=False,listitem=liz)
    xbmc.Player().play(media_url)
    return

def GET_HTML(url,linkback):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link=response.read()
    response.close()
    return link
    

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
        url = 'http://www.awesomedl.com/search?q=%s&x=0&y=0'%(search_entered).replace(' ','+')
        GA("None","SEARCH: "+search_entered)
        INDEX(url,'')


def HELP():
    help = SHOWHELP()
    help.doModal()
    GA("None","MODE: SHOWHELP")
    del help

def GRABMETA(meta_name,types):
    name = meta_name
    print '""""""""""""""""""""""""""""""""""""'
    print name
    type = types
    IMDB = None
    if re.findall(r'\ss[0-9]{2}e[0-9]{2}\s',name,re.I):
        print '=-=-=-=-=-=-=-=-=-=--=-=-=--=-='
        name = re.split(r'\ss[0-9]{2}e',name,re.I)
        print '@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@'
        print name
    if type == 'tvshow':
        #print 'PASSED'
        print name
        if re.findall(r'\sseason\s[0-9]{2}',name,re.I):
            name = re.split(r'\sseason\s[0-9][0-9]',str(name),re.I)
            print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
            print name
        if '-' in name:
            name = name.split('-')
            meta = grab.get_meta(type,name[1].strip(),None,None,None,overlay=6)
        else:
            meta = grab.get_meta(type,name.strip(),None,None,None,overlay=6)
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],
                      'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],
                      'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                      'backdrop_url': meta['backdrop_url'],'status': meta['status'],'imdb_id': meta['imdb_id'],
                      'trailer_url': meta['trailer_url']}
    if type == 'episode':
        if re.findall(r'Season.+?, Episode',name,flags=re.I):
            name = name.replace('Season',':Season ')
            r = name.split(':')
            Se = r[1].replace(' ','')
            t = re.findall(r'Season(.+?),Episode(.+?)',Se,flags=re.I)
            name = r[0].strip()
            meta = grab.get_meta('tvshow',name,None,None,None,overlay=6)
            infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],
                          'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],
                          'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                          'backdrop_url': meta['backdrop_url'],'status': meta['status'],'imdb_id': meta['imdb_id']}
        else:
            infoLabels = {'cover_url': '','title': name}
    if type == None: infoLabels = {'cover_url': '','title': name}
    
    return infoLabels


class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,"%s/resources/art/Help.png"%local.getAddonInfo("path")))
    def onAction(self, action):
        if action == 92 or action == 10:
            xbmc.Player().stop()
            self.close()

def addDir(mode,url,types,linkback,meta_name,name,iconimage):
    if local.getSetting("enable_meta") == "true": infoLabels = GRABMETA(meta_name,types)
    else: infoLabels = {'cover_url': '','title': name }
    if types == None: img = iconimage
    else: img = infoLabels['cover_url']
    u=sys.argv[0]+"?mode="+str(mode)+"&url="+str(url)+"&types="+str(types)+"&linkback="+str(linkback)+"&meta_name="+str(meta_name)+"&name="+str(name)+"&iconimage="+str(iconimage)
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=img)
    liz.setInfo( type="Video", infoLabels= infoLabels)#
    try:
        if types != None:
            liz.setProperty('fanart_image', infoLabels['backdrop_url'])#
    except:
        pass
    if local.getSetting("list_alphabetically") == "true" :
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_TITLE)#needs to check on this
    if linkback == 'latest' and local.getSetting("list_alphabetically") == "true":
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?url=%s&mode=%s&name=%s"%(url,mode,name),isFolder=False,listitem=liz)

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType) )

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
print '----------------------------------------------------'
print 'Mode: '+str(mode)
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
elif mode == 500:
    VIDEO_LINKS(url,name,types)
elif mode == 600:
    WATCH_MEDIA(url,types,linkback)

addon.end_of_directory()
