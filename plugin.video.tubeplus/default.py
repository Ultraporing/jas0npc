
import urllib,urllib2,sys,re,xbmcplugin
import xbmcgui,xbmcaddon,xbmc,base64
import time,datetime,os,urlresolver
import cookielib,unicodedata,HTMLParser

ADDON = xbmcaddon.Addon(id='plugin.video.tubeplus')
sys.path.append( "%s/resources/"%ADDON.getAddonInfo('path') )

from metahandler import metahandlers
from BeautifulSoup import BeautifulSoup
from sqlite3 import dbapi2 as database
from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
addon = Addon('plugin.video.tubeplus', sys.argv)
announce = 'http://jas0npc-xbmc-repository.googlecode.com/svn/trunk/announce/TPLUS_NOTICE.xml'
datapath = addon.get_profile()
grab = metahandlers.MetaData()
net = Net()
BASE_URL = 'http://www.tubeplus.me/'
cookie_path = os.path.join(datapath, 'cookies')                 
cookie_jar = os.path.join(cookie_path, "cookiejar.lwp")
if os.path.exists(cookie_path) == False:                        
    os.makedirs(cookie_path)
print 'TubePlus V2 1.0.3'

def MAIN():
    if ADDON.getSetting('firstrun') == 'true':
        dialog = xbmcgui.Dialog()
        dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I]To get the best results from this addon, Set the [/I]","[I][B]Real-Debrid[/B] priority setting to [B]105[/B] in the [/I]","[I]resolver settings.[/I]")
        dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I]You can dissable this popup in the addon settings[/I]")
    addDir(10,'url','None','','','[B]T[/B]V Shows Menu','%s/resources/art/tvshows.jpg'%ADDON.getAddonInfo("path"))
    addDir(20,'url','None','','','[B]M[/B]ovies Menu','%s/resources/art/movies.jpg'%ADDON.getAddonInfo("path"))
    addSpecial('[COLOR yellow]Resolver Settings[/COLOR]','www.nonsense.com','40','%s/resources/art/settings.jpg'%ADDON.getAddonInfo("path"))
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','50','%s/resources/art/help.jpg'%ADDON.getAddonInfo("path"))
    
def TVMENU():
    addDir(100,'url','None','','','[B]L[/B]atest Aired TV Shows/Episodes','%s/resources/art/latest.jpg'%ADDON.getAddonInfo("path"))
    addDir(115,'url','None','','','[B]T[/B]op 10 Tv Episodes','%s/resources/art/top10.jpg'%ADDON.getAddonInfo("path"))
    addDir(110,'url','None','','','[B]T[/B]V Shows by Genres','%s/resources/art/genres.jpg'%ADDON.getAddonInfo("path"))
    addDir(120,'url','None','','','[B]T[/B]V Shows A to Z','%s/resources/art/az.jpg'%ADDON.getAddonInfo("path"))
    addDir(130,'url','None','','','[B]S[/B]earch TV Shows','%s/resources/art/search.jpg'%ADDON.getAddonInfo("path"))
    
def MOVIEMENU():
    addDir(200,BASE_URL+'browse/movies/Last/ALL/','None','','','[B]M[/B]ost Popular Movies','%s/resources/art/popular.jpg'%ADDON.getAddonInfo("path"))
    addDir(210,'url','None','','','[B]M[/B]ovies By Genres','%s/resources/art/genres.jpg'%ADDON.getAddonInfo("path"))
    addDir(220,'url','None','','','[B]M[/B]ovies by A to Z','%s/resources/art/az.jpg'%ADDON.getAddonInfo("path"))
    addDir(230,'url','None','','','[B]S[/B]earch Movies','%s/resources/art/search.jpg'%ADDON.getAddonInfo("path"))
    
def GET_INDEX(url,types,meta_name):
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait as media is cached.[/I][/COLOR]')#
    html = GETHTML(url)
    r = re.findall(r'title="Watch onli(.+?)></a>',html,flags=re.M)
    r = re.compile(r'ne:\s(.+?)" href="/(.+?)"><img.+?src="/(.+?)"',).findall(str(r))
    totalLinks = len(r)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
    dialogWait.update(0,'[B][I][COLOR yellow] List`s will load much quicker from now on[/B][/I][/COLOR]',remaining_display)#
    for name, urls, image in r:
        name = name.replace('_',' ').replace('/','').replace('\\x92',"'").replace('&rsquo;',"'").replace('&quot;','"').replace('&#044;',',')
        cachedLinks = cachedLinks +1#
        percent = (cachedLinks * 100)/totalLinks#
        remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
        dialogWait.update(percent,'[I][B][COLOR yellow] List`s will load much quicker from now on[/B][/COLOR][/I]',remaining_display)#
        addDir(300,BASE_URL+urls,types,'','',name,'')
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")

def INDEX2(url,types,linkback):
    if linkback == 'movie':
        types = 'movie'
    if linkback =='latesttv'or linkback == 'ATOZ':
        types = 'latesttv'
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait as media is cached.[/I][/COLOR]')#
    html = GETHTML(url)
    r = re.compile(r'<div id="list_body">(.+?)<div id="list_footer"></div>', re.DOTALL|re.I|re.M).findall(html)
    match = re.compile(r'title="Watch online: ([^"]*)" href="/([^"]*)"><img border="0" alt=".+?" src="([^"]*)"></a>', re.I).findall(str(r))# href',str(r),flags=re.I)
    totalLinks = len(match)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
    dialogWait.update(0,'[B][I][COLOR yellow] List`s will load much quicker from now on[/B][/I][/COLOR]',remaining_display)#
    for name, urls, image in match:
        name = name.replace('_',' ').replace('/','').replace('\\x92',"'").replace('&rsquo;',"'").replace('&quot;','"').replace('&#044;',',')
        cachedLinks = cachedLinks +1#
        percent = (cachedLinks * 100)/totalLinks#
        remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
        dialogWait.update(percent,'[I][B][COLOR yellow] List`s will load much quicker from now on[/B][/COLOR][/I]',remaining_display)#
        if types == 'latesttv':
            addDir(350,BASE_URL+urls,types,types,'',name,'')
        if linkback == 'movie':
            types = 'movie'
            addDir(300,BASE_URL+urls,types,types,'',name,'')
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")

def VIDEOLINKS(url,types):
    returl = url
    r = re.findall(r'player/.+?/(.+?)/',url)
    for name in r:
        html = GETHTML(url)
    if "<br><b class='error'>Movie have been removed</b>" in html:
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Movie Removed[/B][/COLOR],TubePlus says Movie Removed,10000,'')")
        return
    if types == 'latesttv' or types =='season2':
        types ='tvshow'
    if ':' in name:
        name = name.split(':')
        name = name[0]
    else:
        name = name
    meta = grab. _cache_lookup_by_name(str(types), str(name),year='')
    infoLabels = {'cover_url': meta['cover_url']}
    r = re.compile(r'class="(o.+?)">.+?javascript:show\(\'(.+?)\'\,\'.+?\'\,\s\'(.+?)\'\)\;.+?<b>(.+?)said work',re.M|re.DOTALL).findall(html)
    sources =[]
    for status, file_id, hoster, said in r:
        percentage = said.replace('%','')
        if int(percentage) in range(0,25):
            title = '[COLOR yellow]'+hoster+'[/COLOR][COLOR red]           '+status+' '+said+'[/COLOR]'
        if int(percentage) in range(25,50):
            title = '[COLOR yellow]'+hoster+'           '+status+' '+said+'[/COLOR]'
        if int(percentage) in range(50,75):
            title = '[COLOR yellow]'+hoster+'[/COLOR][COLOR orange]           '+status+' '+said+'[/COLOR]'
        if int(percentage) in range(75,101):
            title = '[COLOR yellow]'+hoster+'[/COLOR][COLOR green]           '+status+' '+said+'[/COLOR]'
        source = urlresolver.HostedMediaFile(host=hoster, media_id=file_id, title=title)
        sources.append(source)
    urlresolver.filter_source_list(sources)
    source = urlresolver.choose_source(sources)
    try:
        if source: stream_url = source.resolve()
        else: stream_url = ''
        liz=xbmcgui.ListItem(name, iconImage='',thumbnailImage=infoLabels['cover_url'])
        liz.setInfo('Video', {'Title': name} )
        liz.setProperty("IsPlayable","true")
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=stream_url,isFolder=False,listitem=liz)
        xbmc.Player().play(stream_url,liz)
    except:
        xbmc.executebuiltin("XBMC.Notification([COLOR red]Connection Error[/COLOR]Please check status of hoster @real-debrid,10000,''")
        if ADDON.getSetting('firstrun') == 'false' and  ADDON.getSetting('hoster_warning') == 'true':
            dialog = xbmcgui.Dialog()
            dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I][B]DO NOT FORGET TO CHANGE THE REAL-DEBRID[/I][/B]","[I][B]PRIORITY TO 105, THAT WILL REDUCE THE ERRORS![/I][/B]","")
            dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I]You can dissable this popup in the addon settings[/I]","[I]Reminder about REAL-DEBRID priority[/I]")
        return VIDEOLINKS(returl,types)
    
def SEASONS(url,linkback):
    html = GETHTML(url)
    r = re.findall(r'id="l(sea.+?)" class="season"',html,flags=re.DOTALL|re.M)
    for seasons in r:
        season = seasons.replace('_',' ')
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        types = 'season'
        meta_name = 'MN:'+url+':'+season+':'
        addDir(400,url,types,seasons,meta_name,season,'')
    

def SEASONS2(url,types,linkback):
    if types == 'season':
        types = 'season2'
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait as media is cached.[/I][/COLOR]')#
    html = GETHTML(url)
    r = re.compile(r'parts" id="'+linkback+'"><a name=(.+?)<div id="parts_header">',re.M|re.DOTALL).findall(html)
    match = re.compile('href=/(.+?'+linkback+'.+?)">(.+?)</a>').findall(str(r))
    totalLinks = len(match)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
    dialogWait.update(0,'[B][I][COLOR yellow] List`s will load much quicker from now on[/B][/I][/COLOR]',remaining_display)#
    for url, desc in match:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        xbmcplugin.setContent(int(sys.argv[1]), 'movies')
        xbmc.executebuiltin("Container.SetViewMode(503)")
        meta_name = url+';'+desc
        cachedLinks = cachedLinks +1#
        percent = (cachedLinks * 100)/totalLinks#
        remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
        dialogWait.update(percent,'[I][B][COLOR yellow] List`s will load much quicker from now on[/B][/COLOR][/I]',remaining_display)#
        addDir(300,BASE_URL+url,types,linkback,meta_name,desc,'')
    xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
    xbmc.executebuiltin("Container.SetViewMode(504)")
    
def GETHTML(url):
    try:
        #html = net.http_GET(url).content
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:12.2) Gecko/20120605 Firefox/12.2 PaleMoon/12.2')
        response = urllib2.urlopen(req, timeout = 45)
        html=response.read()
        response.close()
        return html
    except Exception, e:
        print "Failed to retrieve page: %s" %url
        print 'Urllib2 error: '+str(e)
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Connection Error[/B][/COLOR],Could not connect to TubePlus,10000,''")
        return MAIN()

def ANNOUNCEMENT(link):
    r = re.findall(r'<title>(.+?)<Etitle><line1>(.+?)<Eline1><line2>(.+?)<Eline2><line3>(.+?)<Eline3>',link,re.I)
    for title, line1, line2, line3 in r:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('[B][COLOR red]'+title+'[/B][/COLOR]','[COLOR red]'+line1+'[/COLOR]','[COLOR red]'+line2+'[/COLOR]','[COLOR red]'+line3+'[/COLOR]')
    return

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

def addDir(mode,url,types,linkback,meta_name,name,iconimage):
    u=sys.argv[0]+"?mode="+str(mode)+"&url="+str(url)+"&types="+str(types)+"&linkback="+str(linkback)+"&meta_name="+str(meta_name)+"&name="+str(name)+"&iconimage="+str(iconimage)
    ok=True
    if ADDON.getSetting("usemeta") == "true": infoLabels = GRABMETA(name,types,meta_name,url)
    else: infoLabels = {'cover_url': "", 'title': name}
    if types == 'None': img = iconimage
    else: img = infoLabels['cover_url']
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=img)
    if types != 'None':
        try:
            liz.setProperty('fanart_image', infoLabels['backdrop_url'])
            liz.setInfo( type="Video", infoLabels = infoLabels )
        except: pass
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def HELP():
    help = SHOWHELP()
    help.doModal()
    del help


class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,"%s/resources/art/Help.png"%ADDON.getAddonInfo("path")))
    def onAction(self, action):
        if action == 92 or action == 10:
            xbmc.Player().stop()
            self.close()

def FIND_IMDB(name):
    name = name.split('-')
    name = name[0].strip()
    meta = grab.get_meta('tvshow',name,None,None,'',overlay=6)
    infoLabels = {'imdb_id': meta['imdb_id']}
    imdb = infoLabels['imdb_id']
    return imdb

def FIND_IMDBB(url):
    html = GETHTML(url)
    r = re.findall(r'<b>IMDB:</b>.+?<span>(.+?)</span>',html,flags = re.M|re.DOTALL)
    if len(r) == 0:
        imdb = 'None'
    else:
        for imdb in r:
            pass
    return imdb
    
def GRABMETA(name,types,meta_name,url):
    name = name+':'
    type = types
    if type == 'None':
        infoLabels = {'cover_url': '','title': name }
        return infoLabels
    if type == 'movie':
        meta = grab.get_meta(type,name,None,None,'',overlay=6)
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],
                      'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url']}
        if infoLabels['cover_url'] == '' : infoLabels['cover_url'] = "%s/resources/art/TVRNoimage.png"%(ADDON.getAddonInfo("path"))

    if type == 'latesttv':
        r = re.compile(r'(.+?)\s-\sSeason:\s(.+?)\sEpisode:\s(.+?)\s-(.+?):').findall(name)
        for name, season, episode, epname in r:
            name = name.replace('_',' ').replace('/','').replace('\\x92',"'").replace('&rsquo;',"'").replace('&quot;','"').replace('&#044;',',')
        if ':' in name:
            name = name.split(':')
            name = name[0].strip()
        imdb = FIND_IMDB(str(name))
        meta = grab.get_meta('tvshow',name,imdb, None, None, overlay=6)
        infoLabels = {'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],
                      'backdrop_url': meta['backdrop_url']}
    if 'MN:' in meta_name:
        r = re.findall(r'player/.+?/(.+)/:season (.+?):',meta_name)
        for name, season in r:
            name = name.replace('_',' ').replace('/','').replace('\\x92',"'").replace('&rsquo;',"'").replace('&quot;','"').replace('&#044;',',')
            meta = grab.get_seasons(name,'',season)
            r = re.findall(r"'cover_url': '(.+?)'",str(meta))
            for thumb in r:
                infoLabels ={'cover_url': thumb, 'title': name}

    if type == 'season2':
        r = re.compile(r'player/.+?/(.+?)/season_(.+?)/episode_(.+?)/').findall(meta_name)
        for name, season, episode in r:
            name = name.replace('%3A',':').split(':')
            name = name[0]
            imdb = FIND_IMDB(name)
            if imdb =='':
                infoLabels = {'cover_url': '','title': name }
            if episode !='0':
                meta = grab.get_episode_meta(name,imdb,int(season),int(episode),episode_title='', overlay=6)
                infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                              'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'studio': meta['studio'],
                              'backdrop_url': meta['backdrop_url']}
            else:
                infoLabels = {'cover_url': '','title': name }
    return infoLabels

def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sys.argv[0]+"?url=%s&mode=%s&name=%s"%(url,mode,name),isFolder=False,listitem=liz)



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
    
elif mode == 10:
    TVMENU()
elif mode == 20:
    MOVIEMENU()

elif mode == 40:
    urlresolver.display_settings()
    MAIN()

elif mode == 50:
    HELP()

elif mode == 100:
    if url =='http://www.tubeplus.me/browse/tv-shows/':
        types ='latesttv'
        meta_name = 'latestaired'
    else:
        url = BASE_URL+'browse/tv-shows/Last/ALL/'
        types ='latesttv'
        meta_name = 'latestaired'
    GET_INDEX(url,types,meta_name)

elif mode == 110:
    url = BASE_URL+'browse/tv-shows/'
    html = GETHTML(url)
    genre = re.findall(r'text: "([^"]*)", css:',html)
    for genre in genre[0:50]:
        url = BASE_URL+'browse/tv-shows/'+genre+'/ALL/'
        addDir(150,url,'None','latesttv','',genre,'')
    
elif mode == 115:
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait as media is cached.[/I][/COLOR]')#
    url = 'http://www.tubeplus.me'
    html = GETHTML(url)
    r = re.compile(r'Top 10 TV Episodes(.+?)<a class="more_vid" href=',re.DOTALL|re.M).findall(html)
    match = re.compile(r'title="Watch online: ([^"]*)" href="([^"]*)"><img border="0" alt=".+?" src="([^"]*)"></a>.+?class="sbtitle">([^"]*)</b>', re.I).findall(str(r))# href',str(r),flags=re.I)
    totalLinks = len(match)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
    dialogWait.update(0,'[B][I][COLOR yellow] List`s will load much quicker from now on[/B][/I][/COLOR]',remaining_display)#
    for name, links, image, seaep in match:
        name = name.replace('\\x92',"'").replace('&rsquo;',"'").replace('&quot;','"')
        name = name+': '+seaep
        cachedLinks = cachedLinks +1#
        percent = (cachedLinks * 100)/totalLinks#
        remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
        dialogWait.update(percent,'[I][B][COLOR yellow] List`s will load much quicker from now on[/B][/COLOR][/I]',remaining_display)#
        addDir(300,BASE_URL+links,'latesttv','','',name,iconimage=BASE_URL+image)
    
elif mode == 120:
    if ADDON.getSetting('tvwarn') == 'true':
        dialog = xbmcgui.Dialog()
        dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I][B][COLOR red]IMPORTANT[/B][/COLOR] Some of the options below could take [/I]","[I]a long time to list, Due to the amount of information[/I]","[I]that gets cached, This only happens ONCE.[/I]")
        dialog.ok("[I]TubePLUS by www.xbmchub.com[/I]", "[I]You can dissable this popup in the addon settings[/I]")

    url = 'http://www.tubeplus.me'
    html = GETHTML(url)
    AZ_DIRECTORIES = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
    url = 'http://www.tubeplus.me/browse/tv-shows/All_Genres/-/'
    addDir(150,url,'None','ATOZ','','0-9','')
    for i in AZ_DIRECTORIES:
        iconimage=i
        name = i
        url = BASE_URL+'browse/tv-shows/All_Genres/%s/'%i
        addDir(150,url,'None','ATOZ','',name,'')
    
elif mode == 130:
    last_search = addon.load_data('tvsearch')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I] SEARCH TubePlus TVShows[/B][/I]')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')# sometimes you need to replace spaces with + or %20#
        addon.save_data('tvsearch',search_entered)
    if search_entered == None or len(search_entered)<1:
        TVMENU()
    else:
        url = 'http://www.tubeplus.me/search/tv-shows/%s/'%(search_entered)
        types = 'None'
        linkback = 'latesttv'
        INDEX2(url,types,linkback)
    
elif mode == 150:
    INDEX2(url,types,linkback)
        
elif mode == 200:
    types = 'movie'
    GET_INDEX(url,types,meta_name)
    
elif mode == 210:
    
    url = BASE_URL
    html = GETHTML(url)
    genre = re.findall(r'text: "([^"]*)", css:',html)
    for genre in genre[2:50]:
        name = genre
        url = 'http://www.tubeplus.me/browse/movies/%s/ALL/'%genre
        addDir(150,url,'None','movie','',name,'')
    


    
elif mode == 220:
    AZ_DIRECTORIES = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y', 'Z']
    url = 'http://www.tubeplus.me/browse/movies/All_Genres/-/'
    addDir(150,url,'None','movie','','0-9','')
    for i in AZ_DIRECTORIES:
        iconimage=i
        name = i
        url = 'http://www.tubeplus.me/browse/movies/All_Genres/%s/'%i
        addDir(150,url,'None','movie','',name,'')
    
elif mode == 230:
    last_search = addon.load_data('moviesearch')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I] SEARCH TubePlus Movies[/B][/I]')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')# sometimes you need to replace spaces with + or %20#
        addon.save_data('moviesearch',search_entered)
    if search_entered == None or len(search_entered)<1:
        MOVIEMENU()
    else:
        url = 'http://www.tubeplus.me/search/movies/"%s"/'%(search_entered)
        types = 'movie'
        GET_INDEX(url,types,meta_name)
elif mode == 300:
    VIDEOLINKS(url,types)
elif mode == 350:
    SEASONS(url,linkback)
elif mode == 400:
    SEASONS2(url,types,linkback)
    
    
        






addon.end_of_directory()
