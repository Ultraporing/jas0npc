import urllib,urllib2,re,cookielib,xbmcplugin,xbmcgui,xbmcaddon,socket,os,shutil,urlresolver,string,xbmc
import HTMLParser,base64,datetime,time
addon = xbmcaddon.Addon(id='plugin.video.tv-release')
sys.path.append( "%s/resources/"%addon.getAddonInfo('path') )

from t0mm0.common.net import Net
from t0mm0.common.addon import Addon
from BeautifulSoup import BeautifulSoup
from metahandler import metahandlers
from sqlite3 import dbapi2 as database

socket.setdefaulttimeout(300)# Bloody tvdb - slow or dead
grab = metahandlers.MetaData(preparezip = False)
net = Net()
Addon = Addon('plugin.video.tv-release', sys.argv)
dropbox = 'https://dl.dropbox.com/u/94360623/My-Repo/AWimages/'
BASE_URL = 'http://tv-release.net/category/'
announce = 'http://jas0npc-xbmc-repository.googlecode.com/svn/trunk/announce/TVR_NOTICE.xml'
ADDON = addon
local = addon

print 'TV-Release v1.1.3'
art = xbmc.translatePath(os.path.join(addon.getAddonInfo('path'), 'resources', 'art'))

def MAIN():
    try:
        link = net.http_GET(announce).content
        ANNOUNCEMENT(link)
    except urllib2.URLError, e:
        pass
    
    if addon.getSetting('firstrun') == 'false':
        dialog = xbmcgui.Dialog()
        dialog.ok("[I]TV-Release brought to you by www.xbmchub.com[/I]", "[I]Just a quick point to help you get the most out of[/I]","[I]TV-Release. TV-Release works best with a premium,[/I]","[I]Real-Debrid account.[/I]")
        dialog.ok("[I]My Thanks goto the following[/I]", "[I]XBMCHUB.com, umOuch, Voinage, Eldorado,  Bstrdsmkr,[/I]","[I]Mikey1234, Spoyser, duquesa,Tuxen and attiadona.[/I]")
        dialog.ok("[I]TV-Release brought to you by www.xbmchub.com[/I]", "[I]I need Help with gfx for this addon,[/I]","[I]If you can or would like to help, Please come to,[/I]","[I]http://www.xbmchub.com And say hi..[/I]")
        addon.setSetting(id='firstrun', value='true')
    addDir(1,'url',None,'','','[B]TV Shows[/B]',iconimage = os.path.join(art,'TVRTV-shows.png'))
    addDir(40,'url',None,'','','[B]Movies[/B]',iconimage = os.path.join(art,'TVRTV-movies.png'))
    addSpecial('[COLOR yellow]Resolver Settings[/COLOR]','www.nonsense.com','10',os.path.join(art,'TVRTV-settings.png'))
    addSpecial('[COLOR blue]Having problems, Need help, Click here[/COLOR]','www.nonsense.com','110',os.path.join(art,'TVRTVhelp.png'))
    
    
def TVFORMAT():
    addDir(2,BASE_URL+'tvshows/tv480p/',None,'tvshows/tv480p/','sort','[B]TV 480p[/B]',iconimage = os.path.join(art,'TVRTV480.png'))
    addDir(2,BASE_URL+'tvshows/tv720p/',None,'tvshows/tv720p/','sort','[B]TV 720p[/B]',iconimage = os.path.join(art,'TVRTV720.png'))
    addDir(2,BASE_URL+'tvshows/tvxvid/',None,'tvshows/tvxvid/','sort','[B]TV Xvid[/B]',iconimage = os.path.join(art,'TVRTVXvid.png'))
    addDir(2,BASE_URL+'tvshows/tvmp4/',None,'tvshows/tvmp4/','sort','[B]TV Mp4[/B]',iconimage = os.path.join(art,'TVRTV-mp4.png'))
    addDir(2,BASE_URL+'tvshows/tvpack/',None,'tvshows/tvpack/','sort','[B]TV Packs[/B]',iconimage = os.path.join(art,'TVRTV-mp4.png'))
    addDir(2,BASE_URL+'tvshows/tv-foreign/',None,'tvshows/tv-foreign/','sort','[B]TV Foreign[/B]',iconimage = '')
    addDir(20,'url',None,'','sort','[B][COLOR orange]TV Search[/B][/COLOR]',iconimage = os.path.join(art,'TVRTVSEARCH.png'))
     
def MOVIEFORMAT():
    addDir(2,BASE_URL+'movies/movies480p/',None,'movies480p','sort','[B]Movies 480p[/B]',os.path.join(art,'TVRmovie480.png'))
    addDir(2,BASE_URL+'movies/movies720p/',None,'movies720p','sort','[B]Movies 720p[/B]',os.path.join(art,'TVRmovie720.png'))
    addDir(2,BASE_URL+'movies/moviesxvid/',None,'moviesxvid','sort','[B]Movies Xvid[/B]',os.path.join(art,'TVRmoviexvid.png'))
    addDir(2,BASE_URL+'movies/moviesforeign/',None,'moviesforeign','sort','[B]Movies Foreign[/B]',iconimage = '')
    
def EPINDEX(url,types):
    if re.search(r'movie',linkback,flags=re.I):
        types = 'movie'
    else: types ='tvshow'
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait as new media is cached.[/I][/COLOR]')#
    html = GET_HTML(url)
    if html == None:
        return
    if '<h2>Under Maintenance</h2>' in html:
        dialog = xbmcgui.Dialog()
        dialog.ok("[I][COLOR yellow]TV-Release brought to you by www.xbmchub.com[/I][/COLOR]", "[I][COLOR red][B]The TV-Release website is under Maintenance[/I][/COLOR][/B]","[B][I][COLOR red]Please Try Again Later[/COLOR][/I][/B]")
        return MAIN()
    match = re.compile(r'height="40px" class="posts_table">(.+?)<table width="100%"', re.DOTALL|re.IGNORECASE|re.MULTILINE).findall(html)
    r = re.compile(r'text-align:left;">.+?<a href="(.+?)".+?font size="2px">(.+?)</font.+?td width="9%">(.+?)<br>(.+?)</td>').findall(str(match))#.+?td width="9%">\n(.+?)<br>(.+?)</td>\n').findall(str(match))
    totalLinks = len(r)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'
    dialogWait.update(0,'[B][I][COLOR yellow] List`s will load much quicker from now on[/B][/I][/COLOR]',remaining_display)
    for url, name, date, time in r:
        name = CLEAN_NAME(url,date,time)
        meta_name = GET_META_NAME(name,types)
        if 'S:' in meta_name:
            meta_name = re.findall('(.+?)(?=S:)',meta_name,flags=re.I)
            meta_name = str(meta_name[0])
        cachedLinks =  cachedLinks +1#
        percent = (cachedLinks * 100)/totalLinks#
        remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'
        dialogWait.update(percent,'[I][B][COLOR yellow] List`s will load much quicker from now on[/B][/COLOR][/I]',remaining_display)
        addDir(3,url,types,linkback,meta_name,name,'')
    if 'zmg_pn_current' in html:
        #current = re.compile(r"zmg_pn_current'>(.+?)</span>\n.+?dar'><a href='(.+?)[\d{3}]/' title=", re.DOTALL|re.IGNORECASE).findall(html)
        current = re.findall(r"zmg_pn_current'>(.+?)</span>\n<span class='zmg_pn_standar'><a href='(.+?page/).+?' title='",html,re.DOTALL|re.M)
        r = re.compile(r"<span class='zmg_pn_separator'>...</span>\n.+?title='Page .+?of .+?'>(.+?)</a>",re.IGNORECASE).findall(html)
        if len(r) ==0:
            r = re.compile(r"<span class='zmg_pn_standar'>.+?e='page.+?of.+?'>(.+?)</a>",re.I).findall(html)
        for last_page in r:
            continue
        for cp, np in current:
            cpn = str(cp)
            cp = int(cp)+1
            cp = str(cp)
            next_page = np+cp+'/'
            addDir(2,next_page,None,linkback,'','[B][COLOR orange] Page '+cpn+' Of '+last_page+' Next Page >>[/B][/COLOR]',iconimage = os.path.join(art,'TVRnextpage.png'))
        if (dialogWait.iscanceled()):#
            return False#
    dialogWait.close()#
    del dialogWait#
    
def VIDEOLINKS(url,types,linkback,meta_name,name):
    if types != None: print 'VIDEOLINKS TYPE: '+types
    html = GET_HTML(url)
    vs = re.compile(r'<tbody>.+?<tr><td class="td_heads">(.+?)</tbody></table>',re.DOTALL|re.IGNORECASE).findall(html)
    test = '=\\'
    vs = str(vs).replace(test,'=')
    match = re.compile(r'\'>(.+?)</a>').findall(vs)
    if len(match) ==1:
        match = re.compile(r'<p><a href="(http.+?)".+?rel="nofollow">http').findall(html)
    if len(match) ==0:
        dialog = xbmcgui.Dialog()
        dialog.ok("[I]TV-Release brought to you by www.xbmchub.com[/I]", "[I]There are no links available at the moment,[/I]","[I]Files could still be uploading to hoster,[/I]","[I]Please try again in a while.[/I]")
        if addon.getSetting('use_ga') == 'true':
            meta_name = str(meta_name).replace('[COLOR]','').replace('[/COLOR yellow]','')
        return EPINDEX(BASE_URL+linkback,types)
    for hosturl in match:
        if re.search(r'.rar|.zip',hosturl,flags=re.I):#
            xbmc.executebuiltin("XBMC.Notification([B][COLOR red]MEDIA NOT PLAYABLE[/B][/COLOR],Files are .rar and not streamable.,10000,os.path.join(art,'TVRrarwarn.png')")
            print 'Media not streamable: '+hosturl
        hoster = re.compile('http://(.+?)/').findall(hosturl)
        desc = DESCCLEAN(hosturl)
        for hoster in hoster:
            hoster = str(hoster).replace('www.','').replace('.com','').replace('.in','').replace('.net','').replace('.in','')
            hoster = '[B][COLOR yellow]'+hoster+':[/B][/COLOR]'+' [I][COLOR yellow]'+desc+'[/COLOR][/I]'
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
        meta_name = GET_META_NAME(name,types).replace('S:','SEASON:').replace('E:','EPISODE:')
        try:
            if urlresolver.HostedMediaFile(url=hosturl, title=hoster):
                addDir(4,hosturl,'tvshow',url,meta_name,hoster,'')
                
        except:
            continue
        
def PLAY(url,types,linkback,meta_name):
    infoLabels = GRABMETA(meta_name, types)
    stream_url = urlresolver.HostedMediaFile(url).resolve()
    if stream_url == False:
        Addon.log('Error while trying to resolve %s' % url)
        return VIDEOLINKS(linkback,types,'',meta_name,meta_name)
    meta_name = '[COLOR yellow]'+str(meta_name).replace('SEASON:',' ').replace('EPISODE:','x')+'[/COLOR]'
    liz=xbmcgui.ListItem(meta_name, iconImage= '', thumbnailImage=infoLabels['cover_url'])
    liz.setInfo( type="Video", infoLabels={ "Title": meta_name} )
    liz.setProperty("IsPlayable","true")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=stream_url,isFolder=False,listitem=liz)#; Addon.resolve_url(stream_url)
    meta_name = str(meta_name).replace('[/COLOR]','').replace('[COLOR yellow]','')
    print meta_name
    xbmc.Player().play(stream_url,liz)
    
    

def SEARCH(url):
    last_search = Addon.load_data('search')
    if not last_search: last_search = ''
    search_entered =''
    keyboard = xbmc.Keyboard(search_entered, '[B][I] SEARCH TV-REALEASE.NET TVShows[/B][/I]')
    last_search = last_search.replace('+',' ')
    keyboard.setDefault(last_search)
    keyboard.doModal()
    if keyboard.isConfirmed():
        search_entered = keyboard.getText().replace(' ','+')# sometimes you need to replace spaces with + or %20#
        Addon.save_data('search',search_entered)
    if search_entered == None or len(search_entered)<1:
        MAIN()
    else:
        url = 'http://tv-release.net/?s="%s"&cat='%(search_entered)
        types = None
        SEARCHRESULTS(url,types)
        
def SEARCHRESULTS(url,types):
    dialogWait = xbmcgui.DialogProgress()#
    ret = dialogWait.create('[COLOR yellow][I]Please wait while checking search results.[/I][/COLOR]')#
    if 'aHR0' in url:
        cleanurl = base64.b64decode(url)
        url = cleanurl
    html = GET_HTML(url)
    linkback = url#
    r = re.compile('\?s=(.+?)&',re.I).findall(url)
    for search in r:
        search = str(search).replace('+','-').replace('"','')
    match=re.compile(r'rel="category(.+?)</tr>\n</table>', re.DOTALL|re.I|re.M).findall(html)
    #print 'match: '+match
    totalLinks = len(match)#
    cachedLinks = 0#
    remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
    dialogWait.update(0,'[B][I][COLOR yellow]Please wait while checking search results[/B][/I][/COLOR]',remaining_display)#
    match = str(match).replace('\\n','')
    r = re.findall(r'tag">(.+?)</a></span.+?a\shref="(.+?)">',str(match),re.DOTALL)
    for tag, turl in r:
        if re.search(search,turl,flags=re.I) and tag == 'TV/XviD' or tag == 'TV/Foreign' or tag == 'TV/480p' or tag == 'TV/720p' or tag =='TV/Mp4':
            url = turl
            name =url.rpartition('/')
            name = name[2]
            name = str(name).replace('-',' ')
            meta_name = GET_META_NAME(name,types).replace('S:','SEASON:').replace('E:','EPISODE:')
            cachedLinks = cachedLinks +1#
            percent = (cachedLinks * 100)/totalLinks#
            remaining_display = '[B][COLOR green]Caching '+str(cachedLinks)+' Of  '+str(totalLinks)+'.[/B][/COLOR]'#
            dialogWait.update(percent,'[I][B][COLOR yellow]Please wait while checking search results[/B][/COLOR][/I]',remaining_display)#
            xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
            addDir(3,turl,'tvshow',linkback,meta_name,name,'')
        if (dialogWait.iscanceled()):#
            return False#
    dialogWait.close()#
    del dialogWait#
    if 'zmg_pn_br_after_loop' in html:
        curent_page = re.findall(r'zmg_pn_current\'>(.+?)</span>', html,re.I)
        curentP = ''.join(curent_page)
        cp = int(curent_page[0])+1
        cp = str(cp)
        last_page = re.findall(r'[\d{2}]\'>([\d{2}])</a></span>\n</div>',html)
        lp = ''.join(last_page)
        search = re.findall(r"zmg_pn_standar'><a href='.+?page/.+?\?s=(.+?)(?=\&cat' title='Page.+?</a></span>\n</div>)",html)
        searc = ''.join(search).replace('%5C','').replace('%22','')
        urlt = 'http://tv-release.net/page/'+cp+'/?s="'+searc+'"&cat'.replace('-','+')
        crapurl = base64.b64encode(urlt)
        name = '[B][COLOR orange] Page '+curentP+' Of '+lp+' Next Page >>[/B][/COLOR]'
        addDir(30,crapurl,None,'search','',name,os.path.join(art,'TVRnextpage.png'))
        
def GRABMETA(meta_name,types):
    type = types
    if type != None: print 'NAME AT START OF GRABMETA: '+meta_name+'TYPE: '+type
    if type == 'movie': print 'MOVIE META NAME: '+meta_name
    if 'craig ferguson' in meta_name:
        meta_name = 'The Late Late Show with '+meta_name
    if 'david letterman' in meta_name:
        meta_name = 'Late Show with '+meta_name
    if 'jay leno' in meta_name:
        meta_name = 'The Tonight Show with '+meta_name
    if 'jimmy fallon' in meta_name:
        meta_name = 'Late Night with '+meta_name
    if type == None: infoLabels = {'cover_url': '','title': name}
    elif 'tvshow' in type:
        if 'SEASON:' in meta_name:#
            blob = meta_name.replace('SEASON:',':').replace('EPISODE:',':').split(':')
            meta_name = str(blob[0])
            
        meta_name = re.split(r'[0-9][0-9][0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]',meta_name,2)
        meta_name = str(meta_name[0])
        if 'jimmy kimmel' in meta_name:
            meta_name = meta_name+' Live'
        year = None
        meta = grab.get_meta(type,meta_name,None, None, year, overlay=6)
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'imdb_id': meta['imdb_id'],
                      'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                      'backdrop_url': meta['backdrop_url'],'status': meta['status']}
        print meta_name+' IMDB NO: '+str(infoLabels['imdb_id'])
        if infoLabels['cover_url'] == '' :infoLabels['cover_url'] = infoLabels['banner_url'] #'%s/art/TVRNoimage.png'%addon.getAddonInfo("path")
    elif 'episode' in type:
        try:
            if re.findall('.+?([0-9][0-9][0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]).+?',meta_name):
                blob = re.split(r'[0-9][0-9][0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]',meta_name)
                date = re.findall('.+?([0-9][0-9][0-9][0-9]\s[0-9][0-9]\s[0-9][0-9]).+?',meta_name)
                date = str(date[0]).replace(' ','-')
                blob = str(blob[0])
                if 'jimmy kimmel' in blob:
                    blob = blob+' Live'
                meta = grab.get_episode_meta(blob,None,int('1'),int('0'),air_date=date,overlay='6')
                infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],'imdb_id': meta['imdb_id'],
                      'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                      'backdrop_url': meta['backdrop_url'],'status': meta['status']}
                
                if infoLabels['cover_url'] == '' : infoLabels['cover_url'] = os.path.join(art,'TVRNoimage.png')
                #if infoLabels['backdrop_url'] =='': infoLabels['backdrop_url'] ='%s/resources/art/xbmcback.png'%addon.getAddonInfo("path")

        except:
            pass
        try:
            
            if 'SEASON:' in meta_name:
                blob = meta_name.replace('SEASON:',':').replace('EPISODE:',':').split(':')
                meta = grab.get_episode_meta(blob[0].strip(),None,int(blob[1].strip()),int(blob[2].strip()),overlay='6')
                infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'cover_url': meta['cover_url'],
                      'cast': meta['cast'],'studio': meta['studio'],'banner_url': meta['banner_url'],
                      'backdrop_url': meta['backdrop_url'],'status': meta['status']}
                if infoLabels['cover_url'] == '' : infoLabels['cover_url'] = os.path.join(art,'TVRNoimage.png')

        except:
            pass
        try:
            if infoLabels['plot'] =='' and 'SEASON:' in meta_name:
                blob = meta_name.replace('SEASON:',':').replace('EPISODE:',':').split(':')
                meta = grab._cache_lookup_by_name('tvshow',blob[0].strip(), year='')
                infoLabels = {'genre': meta['genre'],'cover_url': meta['cover_url'],'banner_url': meta['banner_url'],
                              'backdrop_url': meta['backdrop_url'],'title': meta['title'],'tvdb_id': meta['tvdb_id']}
            if infoLabels['cover_url'] =='':
                infoLabels['cover_url'] = infoLabels['banner_url']
            if infoLabels['cover_url']=='':
                infoLabels['cover_url'] = infoLabels['backdrop_url']
            
        except:
            pass
    elif 'movie' in type:
        r = re.split(r'480p|720p|xvid',meta_name,0,)
        tname = re.findall(r'(.+?)\s[\d]{4}',r[0],flags=re.I)
        year = re.findall(r'([\d{4}])',r[0])
        if len(tname) >=1:
            tname=tname[0]
        tname =''.join(tname)
        year =''.join(year)
        meta = grab.get_meta(type,tname,None,None,year,overlay='6')
        infoLabels = {'rating': meta['rating'],'duration': meta['duration'],'genre': meta['genre'],'mpaa':"rated %s"%meta['mpaa'],
                      'plot': meta['plot'],'title': meta['title'],'writer': meta['writer'],'cover_url': meta['cover_url'],
                      'director': meta['director'],'cast': meta['cast'],'backdrop_url': meta['backdrop_url'],'imdb_id': meta['imdb_id']}
    if infoLabels['cover_url'] =='': infoLabels['cover_url'] =os.path.join(art,'TVRNoimage.png')
    return infoLabels            
    
def CLEAN_NAME(url,date,time):
    date = str(date).replace('\\n','')
    try:
        name = re.findall(r'.+?//.+?/(.+?)/',url)
        name =str(name[0])
    except:
        name = str(url).rpartition('/')
        name = name[2]
    name = re.split('x264',name,1)
    name = name[0].replace('-',' ')
    name = name.replace('.',' ').replace('web dl','WEB-DL').replace('hdtv','HDTV').replace('WEB-DL','[B][I][COLOR yellow]WEB-DL[/I][/B][/COLOR]').replace('HDTV','[B][COLOR red]*HDTV*[/B][/COLOR] [COLOR green]ADDED: '+date+' '+time+'[/COLOR]')
    if 'HDTV' not in name:
        name = name+' [COLOR green]ADDED: '+date+' '+time+'[/COLOR]'
    return name

def GET_META_NAME(name,types):
    if 's[0-9][0-9]e[0-9][0-9]' not in name:
        meta_name = name
    try:
        if re.search('s[\d{2}]',name,flags=re.I):
            season, episode = re.findall(r's[0-9][0-9]|e[0-9][0-9]',str(name), flags=re.I)
            season = season.replace('s','S:')
            episode = episode.replace('e','E:')
            meta_name = re.findall('(.+?)(?=S[0-9][0-9])',name,flags=re.I)
            meta_name = meta_name[0]+season+episode
    except:
        meta_name = name
    return meta_name

def GET_HTML(url):
    error_pic = os.path.join(art,'TVRnetwork.png')
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
        xbmc.executebuiltin("XBMC.Notification([B][COLOR red]Connection Error[/B][/COLOR],Could not connect to TV-Release.net,10000,error_pic")
        return MAIN()
    
def ANNOUNCEMENT(link):
    print 'ANNOUNCE'
    r = re.findall(r'<title>(.+?)<Etitle><line1>(.+?)<Eline1><line2>(.+?)<Eline2><line3>(.+?)<Eline3>',link,re.I)
    print r
    for title, line1, line2, line3 in r:
        dialog = xbmcgui.Dialog()
        ok = dialog.ok('[B][COLOR red]'+title+'[/B][/COLOR]','[COLOR red]'+line1+'[/COLOR]','[COLOR red]'+line2+'[/COLOR]','[COLOR red]'+line3+'[/COLOR]')
    return
    
    
def HELP():
    help = SHOWHELP()
    help.doModal()
    del help

def RMOVIEMETA(meta_name):
    imdb_id = Addon.queries.get('imdb_id', '')
    r = re.split(r'480p|720p|xvid',meta_name,0,)
    name = re.findall(r'(.+?)\s[\d]{4}',r[0],flags=re.I)
    year = re.findall(r'([\d{4}])',r[0])
    print str(name)
    if len(name) >=1:
        name = name[0]
    name =''.join(name)
    year =''.join(year)
    metaget=metahandlers.MetaData()
    try:
        search_meta = metaget.search_movies(name)
    except:
        xbmc.executebuiltin("XBMC.Notification([COLOR red]Notice[/COLOR],Could not find correct MetaData,10000,os.path.join(art,'TVRnotify.png')")

        return

    if search_meta:
        movie_list = []
        for movie in search_meta:
            movie_list.append(movie['title'] + ' (' + str(movie['year']) + ')')
        dialog = xbmcgui.Dialog()
        index = dialog.select('Choose', movie_list)

        if index > -1:
            new_imdb_id = search_meta[index]['imdb_id']
            new_tmdb_id = search_meta[index]['tmdb_id']       
            meta = metaget.update_meta('movie', name, imdb_id=imdb_id, new_imdb_id=new_imdb_id, new_tmdb_id=new_tmdb_id, year=year)   
            xbmc.executebuiltin("Container.Refresh")
    else:
        msg = ['No matches found']
        Addon.show_ok_dialog(msg, 'Refresh Results')

def DESCCLEAN(hosturl):
    print 'DESCCLEAN: '+hosturl
    descc = hosturl.rpartition('/')
    descc = descc[2].replace('.html', '')
    descc = descc.replace('.htm', '')
    descc = descc.replace ('-',' ')
    descc = descc.replace('_',' ')
    descc = descc.replace('.',' ')
    return descc
    

def SEARCHTRAILER(meta_name,url):
    name = re.findall(r'(.+?)(?=\s[0-9]{4}\s)',meta_name)
    year = re.findall(r'.+?([0-9]{4}).+?',meta_name)
    year = ''.join(year)
    name = ''.join(name).replace('-',' ').strip()
    search = name.strip()
    res_name = []
    res_url = []
    search = '"'+search+' '+year+' Official Trailer hd site:youtube.com"'
    search = search.replace(' ','+')
    html = GET_HTML('http://www.google.com/search?q='+search)
    r = re.compile(r'cite class="kv">(www.youtube.com.+?<)/cite>',re.I).findall(str(html))
    ytid = re.compile(r'watch\?v=(.+?)<').findall(str(r))
    try:
        xbmc.executebuiltin(
            "PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid=%s)"
            %ytid[1])
    except:
        print "Failed to find trailer for: %s" %name
        xbmc.executebuiltin("XBMC.Notification([COLOR red]Trailer Error[/COLOR],No trailer found,10000,os.path.join(art,'warning.png')")
        



class SHOWHELP(xbmcgui.Window):
    def __init__(self):
        self.addControl(xbmcgui.ControlImage(0,0,1280,720,os.path.join(art,'Help.png')))
    def onAction(self, action):
        if action == 92 or action == 10:
            self.close()


            
        
#----------------------------------------------------------------------------------------------------------------
"""Create boxset module between the lines"""
def CREATE_BOXSET(meta_name,url):
    boxset_path = os.path.join(Addon.get_profile(), 'boxset')
    boxset = os.path.join(boxset_path, meta_name)
    if os.path.exists(boxset_path) == False:
        os.makedirs(boxset_path)
    if os.path.exists(boxset) == False:
        os.makedirs(boxset)
    meta_name = meta_name.strip()
    url = 'http://tv-release.net/?s="%s"&cat='%(meta_name).replace(' ','+')
    html = GET_HTML(url)
    print 'CBS PATH: '+addon.getAddonInfo("path")
    print 'CBS DPATH: '+Addon.get_profile()
    print 'CBS BOXSET PATH: '+boxset_path
    print 'BOXSET NAME: '+boxset

    #-----------------------------------------------------------------------
    print 'Create Boxset MetaName: '+meta_name
    print 'Create Boxset url: '+url
    if re.search(r'\s[0-9]{4}\s[0-9]{2}\s[0-9]{2}\s',meta_name,flags=re.I):
        print 'YES: Meta_name: '+meta_name

    print 'meta_name2: '+meta_name
    print 'CBS URL: '+url
    #-----------------------------------------------------------------------



    
#--------------------------------------------------------------------------------------------------------------------
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
    infoLabels = GRABMETA(meta_name, types)
    if types == None: img = iconimage
    else: img = infoLabels['cover_url']
    if types != None and len(img)==0:
        if infoLabels['cover_url'] =='':
            img = infoLabels['banner_url']
    liz=xbmcgui.ListItem(name, iconImage = infoLabels['cover_url'], thumbnailImage = img)
    if types == 'movie':
        liz.addContextMenuItems([('[COLOR yellow]Refresh Movie Metadata [/COLOR]',"XBMC.RunPlugin(%s?mode=%s&meta_name=%s&url=%s)"%(sys.argv[0],120,meta_name,url)),
                                 ('[COLOR yellow]Play Movie Trailer[/COLOR]',"XBMC.RunPlugin(%s?mode=%s&meta_name=%s&url=%s)"%(sys.argv[0],130,meta_name,url)),
                                 ('[COLOR yellow]Movie Information[/COLOR]', 'XBMC.Action(Info)')], replaceItems = True)
 
        
    if types == None:
        liz.setProperty('fanart_image', os.path.join(art,'xbmcback.png'))
    else: liz.setProperty('fanart_image', infoLabels['backdrop_url'])
    liz.setInfo("Video", infoLabels);ok=True
    if 'search'  in linkback:
        xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok

def addSpecial(name,url,mode,image):
    liz=xbmcgui.ListItem(label = '[B]%s[/B]'%name,iconImage="",thumbnailImage = image)
    liz.setProperty('fanart_image', os.path.join(art,'xbmcback.png'))
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
elif mode == 1:
    TVFORMAT()
elif mode == 2:
    EPINDEX(url,types)
elif mode == 3:
    VIDEOLINKS(url,types,linkback,meta_name,name)
elif mode == 4:
    PLAY(url,types,linkback,meta_name)
elif mode == 10:
    urlresolver.display_settings()
elif mode == 20:
    SEARCH(url)
elif mode == 30:
    SEARCHRESULTS(url,types)
elif mode == 40:
    MOVIEFORMAT()
elif mode == 100:
    CREATE_BOXSET(meta_name,url)
elif mode == 110:
    HELP()
elif mode == 120:
    RMOVIEMETA(meta_name)
elif mode == 130:
    print '130'+meta_name
    SEARCHTRAILER(meta_name,url)
xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=True)
