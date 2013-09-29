import os,xbmcplugin,xbmcgui,xbmcaddon,xbmc
import urllib,urllib2,re,sys,string,time,datetime

error_logo  = xbmc.translatePath('special://home/addons/plugin.video.moviekingdom/resources/art/redx.png')
try:
    import urlresolver
    from addon.common.addon import Addon
    from addon.common.net   import Net as net
    from metahandler        import metahandlers
    from BeautifulSoup      import BeautifulSoup
    from universal          import favorites, watchhistory, playbackengine
except Exception, e:
    xbmc.executebuiltin("XBMC.Notification([COLOR blue]Movie Kingdom Error[/COLOR],[COLOR blue]Failed To Import Needed Modules Check Log For Details[/COLOR],7000,"+error_logo+")")
    xbmc.log('Movie Kingdom ERROR - Importing Modules: '+str(e))
    sys.exit(0)


addonID = 'plugin.video.moviekingdom'
addon = Addon(addonID, sys.argv)   #t0mm0 addon Initialization
datapath = xbmc.translatePath(addon.get_profile())
local = xbmcaddon.Addon(id=addonID)#xbmc addon Initialization
baseUrl = 'http://www.movie-kingdom.com/'
grab = metahandlers.MetaData()
sys.path.append(xbmc.translatePath(os.path.join( local.getAddonInfo('path'), 'resources', 'lib' ))) 
userAgent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
fav = favorites.Favorites(addonID, sys.argv)
downloadPath = local.getSetting('download-folder')
DownloadLog=os.path.join(datapath,'Downloads')
try:os.makedirs(DownloadLog)
except:pass
DownloadFile=os.path.join(DownloadLog,'DownloadLog')




def MAIN():#addDir(mode,url,types,meta_name,name,iconimage,totalItems,imdb,special,queued)
    addDir(10, baseUrl+'new-shows/', None, None, 'TV - Latest Added Episodes', '', 0, 'TVE', None, '')
    addDir(11, baseUrl, None, None, 'TV - Random Tv Shows', '', 0, 'TVR', None, '')
    addDir(14, baseUrl, None, None, 'TV - By Genres', '', 0, 'TVG', None, '')
    addDir(15, baseUrl+'a-z-shows.php', None, None, 'TV - By A To Z', '', 0, 'TVA', None, '')
    addDir(mode, None, None, None, '[COLOR blue]--------------------------------------------------------------------------[/COLOR]', '', 0, '', True, '')
    addDir(30, baseUrl+'new-movies/', None, None, 'Movies - Latest Added', '', 0, 'MVA', None, '')
    addDir(30, baseUrl, None, None, 'Movies - Featured Movies', '', 0, 'MVF', None, '')
    addDir(11, baseUrl, None, None, 'Movies - Random Movies', '', 0, 'MVR', None, '')
    addDir(14, baseUrl, None, None, 'Movies - By Genres', '', 0, 'MVG', None, '')
    addDir(15, baseUrl+'a-z-movies.php', None, None, 'Movies - By A To Z', '', 0, 'MVZ', None, '')
    addDir(mode, None, None, None, '[COLOR blue]--------------------------------------------------------------------------[/COLOR]', '', 0, '', True, '')
    #addDir(40, baseUrl+'pages/music', None, None, 'Music - Stream Albums From MovieKingdom', '', 0, 'MUS', None, '')
    addDir(200, None, None, None, 'Search', '', 0, 'SR', None, '')
    

def TvEpisodes(url, imdb):
    html = OpenUrl(url)
    if imdb == 'TVE':
        pattern = 'tons\"\>\n.+?\<a\shref=\"(.+?)\".+?php\?src=(.+?)\&'
        r = re.findall(pattern, html, re.I|re.M|re.DOTALL)
    elif imdb == 'TVS':
        pattern = 'class=\"buttons\"\>\n.+?\<a\shref=\"(.+?)"\srel=\"bookmark\"\stitle=\".+?\"\>\n.+?\<img\ssrc=\".+?php\?src=(.+?)\&'
        r = re.findall(r''+pattern+'', html, re.I|re.M|re.DOTALL)
        print 'tvep TVS'
        print r
    totalitems = len(r)
    for url, img in r:
        print url
        if re.findall('season/\d+/episode/\d+', url, re.I):
            r = re.split('com/show/', url.replace('-', ' ').replace('/sea', ': Sea'))
            name = re.sub(r'/', ' ', r[1]).title()
            addDir(20, url, 'episode', name, name, img, totalitems, imdb,'', '')

def Random(url, imdb):
    html = OpenUrl(url)
    if imdb == 'TVR':
        types = 'tvshow'
        mode = '13'
        pattern = 'imageWrapper\"\>\n.+?\<a\shref=\"(http:\/\/www\.movie-kingdom\.com\/show\/.+?)\"\sclass.+?php\?src=(.+?)\&'
        urlP = 'show'
    elif imdb == 'MVR':
        types = 'movie'
        html = re.findall(r'e">Random Movies</h3>(.+?)e">Random TV Shows</h3>', html, re.I|re.DOTALL)[0]
        pattern = 'imageWrapper\"\>.+?\<a\shref="(http\:\/\/www.movie-kingdom.com\/movie/.+?)"\s+class=\"\"\>.+?src.+?php\?src=(.+?)\&'
        urlP = 'movie'
        mode = '20'
    r = re.findall(r''+pattern+'', html, re.I|re.M|re.DOTALL)
    totalitems = len(r)
    for url, img in r:
        name = re.findall(r'.com/'+urlP+'/(.+)', url.replace('-',' '))[0].title()
        addDir(mode, url, types, name, name, '', totalitems, imdb, None, None)

    

def TvSeason(url, meta_name, imdb):
    html = OpenUrl(url)
    pattern = 'value=\"(.+?)\"\>(Season\s\d+)\<\/option\>'
    r = re.findall(r''+pattern+'', html)
    totalitems = len(r)
    for url, season in r:
        r = re.findall(r'\/show\/(.+?)\/', url.replace('-', ' ').title(), re.I)
        name = r[0]+': '+season
        addDir(10, url, 'season', url.title(), name.title(), '', totalitems, 'TVS', None, None)
    #setView('season', 'season')

def Genre(url, imdb):
    res_genre = []
    res_url = []
    html = OpenUrl(url)
    if 'TVG' in imdb:pattern = 'href=\"(http:\/\/www.movie-kingdom.com\/tv-tags\/\w+)\"\sstyle'
    elif 'MVG' in imdb:pattern = 'href=\"(http:\/\/www.movie-kingdom.com\/movie-tags\/\w+)\"\sstyle'
    r = re.findall(r''+pattern+'', html, re.I)
    for url in r:
        r = url.rpartition('/')
        name = r[2].title()
        res_genre.append(name)
        res_url.append(url)
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Please Select Genre',res_genre)

    if ret == -1:MAIN()
    genreUrl = res_url[ret]
    html = BeautifulSoup(net(userAgent).http_GET(genreUrl).content).prettify
    soup = BeautifulSoup(str(html))
    a = soup.findAll("div", {"class": "buttons"})
    if 'TVG' in imdb:pattern = '\<\/div\>,\s\<div\sclass=\"buttons\"\>\n\<a\shref=\"(.+?)\".+?php\?src=(.+?)\&'
    elif 'MVG' in imdb:pattern = '\<\/div\>,\s\<div\sclass=\"buttons\"\>\n\<a\shref=\"(.+?)\".+?php\?src=(.+?)\&'
    r = re.findall(r''+pattern+'', str(a), re.I|re.M|re.DOTALL)
    totalitems = len(r)
    for url, img in r:
        name = url.rpartition('/')
        name = name[2].replace('-', ' ').title()
        if '.com/show/' in url:
            types = 'tvshow'
            mode = '13'
        elif '.com/movie/' in url:
            types = 'movie'
            mode = '20'
        addDir(mode, url, types, name, name, img, totalitems, imdb, None, None)

def MoviesLatest(url, imdb):
    html = OpenUrl(url)
    if 'MVA' in imdb:
        pattern = 'tons\"\>\n.+?\<a\shref=\"(.+?)\".+?php\?src=(.+?)\&'
        r = re.findall(r''+pattern+'', html, re.I|re.M|re.DOTALL)
        t = set(r)
        r = tuple(t)
    elif 'MVF' in imdb:
        temp = re.findall('\<h3\>Featured\sMovies\<\/h3\>(.+?)\<\!-- This\sis\sthe\sb', html, re.I|re.M|re.DOTALL)
        r = re.findall('\<li\>.+?<h2\>.+?\<a\shref=\"(.+?)\"\stitle.+?php\?src=(.+?)\&', str(temp), re.I|re.M|re.DOTALL)
        t = re.findall('</span>.+?<a\shref=\"(.+?)\"\stitle.+?php\?src=(.+?)\&', str(temp), re.I|re.M|re.DOTALL)
        r = r+t
    totalitems = len(r)
    for url, img in r:
        name = re.findall(r'.com\/movie\/(.+?)\"', url+'"', re.I)[0]
        addDir(20, url, 'movie', name.replace('-', ' ').title(), name.replace('-', ' ').title(), img, totalitems, imdb, None, '')
        
def MusicIndex(url, imdb):
    print 'music'
    print url
    print imdb

def Search(url, imdb):
    if imdb == 'SRO':
        search = url.lower().strip().replace(' ', '-')
        html = BeautifulSoup(net(userAgent).http_GET('http://www.movie-kingdom.com/a-z-movies.php').content).prettify
        r = re.findall('\<a\shref=\"(\S+'+search+'\S+)\"\sti', str(html), re.I)
        html = BeautifulSoup(net(userAgent).http_GET('http://www.movie-kingdom.com/a-z-shows.php').content).prettify
        t = re.findall('href="(\S*'+search+'\S*)"', str(html), re.I)
        r = r+t
        totalitems = len(r)
        for url in r:
            name = url.rpartition('/')
            name = name[2].replace('-', ' ').strip().title()
            if '.com/show/' in url:
                addDir(13, url, 'tvshow', name, '[COLOR blue]TV:[/COLOR]'+name, '', totalitems, 'TVR',False, '')
            elif '.com/movie/' in url:
                addDir(20, url, 'movie', name, '[COLOR blue]MOVIE:[/COLOR]'+name, '', totalitems, 'MVR', False, '')
                
    elif imdb == 'SR':
        searchType = ['By Name', 'By Year', 'By Director', 'By Actor']
        dialog = xbmcgui.Dialog()
        ret = dialog.select('Choose How To Search', searchType)
        if ret == -1:MAIN()
        searchtype = searchType[ret]

        if ret == 0:
            url = 'http://www.movie-kingdom.com/index.php?menu=search&query='
            last_search = addon.load_data('search')
            if not last_search: last_search = ''
            search =''
            keyboard = xbmc.Keyboard(search, '[B]SEARCH Movie-kingdom By Name[/B]'.title())
            last_search = last_search.replace('-',' ')
            keyboard.setDefault(last_search)
            keyboard.doModal()
            if keyboard.isConfirmed():
                search = keyboard.getText().replace(' ','-')
                addon.save_data('search', search)
                if search == None or len(search)<1:MAIN()
                html = BeautifulSoup(net(userAgent).http_GET('http://www.movie-kingdom.com/a-z-movies.php').content).prettify
                r = re.findall('\<a\shref=\"(\S+'+search+'\S+)\"\sti', str(html), re.I)
                html = BeautifulSoup(net(userAgent).http_GET('http://www.movie-kingdom.com/a-z-shows.php').content).prettify
                t = re.findall('href="(\S*'+search+'\S*)"', str(html), re.I)
                r = r+t

        if ret == 1:
            url = 'http://www.movie-kingdom.com/index.php?menu=search&year='
            search = xbmcgui.Dialog().numeric(0, '[B]SEARCH By Year[/B]'.title())
            if len(search)!= 4:
                dialog = xbmcgui.Dialog()
                dialog.ok("[B]SEARCH ERROR[/B]", "Search by year date MUST be four numbers long.","eg. 1998, 2011, 2013 only.","")
                Search('','SR')
            html = net(userAgent).http_GET(url+search).content
            pattern = '\"buttons\"\>.+?\<a\shref="(.+?)\"'
            r = re.findall(r''+pattern+'', html, re.I|re.DOTALL)

        if ret == 2:
            url = 'http://www.movie-kingdom.com/index.php?menu=search&director='
            last_search = addon.load_data('search')
            if not last_search: last_search = ''
            search =''
            keyboard = xbmc.Keyboard(search, '[B]SEARCH By director[/B]'.title())
            last_search = last_search.replace('-',' ')
            keyboard.setDefault(last_search)
            keyboard.doModal()
            if keyboard.isConfirmed():
                search = keyboard.getText().replace(' ','-')
                addon.save_data('search', search)
                if search == None or len(search)<1:MAIN()
                html = net(userAgent).http_GET(url+search).content
                pattern = '\"buttons\"\>.+?\<a\shref="(.+?)\"'
                r = re.findall(r''+pattern+'', html, re.I|re.DOTALL)

        if ret == 3:
            url = 'http://www.movie-kingdom.com/index.php?menu=search&star='
            last_search = addon.load_data('search')
            if not last_search: last_search = ''
            search =''
            keyboard = xbmc.Keyboard(search, '[B]SEARCH By Actor[/B]'.title())
            last_search = last_search.replace('-',' ')
            keyboard.setDefault(last_search)
            keyboard.doModal()
            if keyboard.isConfirmed():
                search = keyboard.getText().replace(' ','-')
                addon.save_data('search', search)
                if search == None or len(search)<1:MAIN()
                html = net(userAgent).http_GET(url+search).content
                pattern = '\"buttons\"\>.+?\<a\shref="(.+?)\"'
                r = re.findall(r''+pattern+'', html, re.I|re.DOTALL)

        totalitems = len(r)
        for url in r:
            name = url.rpartition('/')
            name = name[2].strip().replace('-', ' ').title()
            if '.com/show/' in url:
                addDir(13, url, 'tvshow', name, '[COLOR blue]TV:[/COLOR]'+name, '', totalitems, 'TVR',False, '')
            elif '.com/movie/' in url:
                addDir(20, url, 'movie', name, '[COLOR blue]MOVIE:[/COLOR]'+name, '', totalitems, 'MVR', False, '')
    
def AtoZ(url, imdb):
    res_name = []
    res_letter = []
    res_name.append('#1234')
    res_letter.append('#1234')
    for l in string.uppercase:
        res_name.append(l.title())
        res_letter.append(l.title())
    dialog = xbmcgui.Dialog()
    ret = dialog.select('Select The Letter', res_name)
    if 'TVA' in imdb:
        cat = 'show/'
        types = 'tvshow'
        mode = '13'
    if 'MVZ' in imdb:
        cat = 'movie/'
        types = 'movie'
        mode = '20'

    if ret == -1:MAIN()
    letter = res_letter[ret]
    if '#1234' in letter: pattern = 'a\shref=\"('+baseUrl+cat+'\d.+?)\" title'
    else: pattern = 'a\shref=\"('+baseUrl+cat+letter+'.+?)\" title'
    html = net(userAgent).http_GET(url).content
    r = re.findall(pattern, html, re.I|re.M)
    totalitems = len(r)
    for url in r:
        name = url.rpartition('/')[2].replace('-', ' ').title()
        addDir(mode, url, types, name, name, '', totalitems, imdb, None, '')
    
def ListHosts(url, name, imdb):
    originalName = name
    sources = []
    html = BeautifulSoup(net(userAgent).http_GET(url).content).prettify
    soup = BeautifulSoup(str(html))
    a = soup.findAll("span", {"class": "embed-out-link"})
    pattern = 'http://adf.ly/\d+/(.+?)\"'
    r = re.findall(pattern, str(a), re.I)
    for url in r:
        if 'www' in url: url = 'http://'+url
        else: url = 'http://www.'+url
        hosted_media = urlresolver.HostedMediaFile(url=url, title=name)
        sources.append(hosted_media)
    sources = urlresolver.filter_source_list(sources)
    r = re.findall(r'url\'\: \'(.+?)\', \'host', str(sources))
    totalitems = len(r)
    hoster = []
    if 'DM' in imdb:
        for url in r:
            name = re.findall(r'\.(\w+)\.', url)[0].title()
            hoster.append(url)
        return (hoster)

    else:
        for url in r:
            name = re.findall(r'\.(\w+)\.', url)[0].title()
            addDir(100, url, None, originalName, name, '', totalitems, imdb+'HL', True, None)

def WatchTrailer(url):
    html = net(userAgent).http_GET(url).content
    pattern = '<div id="trailers" style="margin-bottom:-15px"></div>\n.+?<script type="text/javascript" src="(.+?)">.+?</script>'
    r = re.findall(r''+pattern+'', html, re.I|re.M|re.DOTALL)
    for url in r:
        html = net(userAgent).http_GET(url).content
        pattern = '\"media\$player\"\:\[\{\"url\"\:\"(.+?)\&feat'
        r = re.findall(r''+pattern+'', html)
        try:trailer_url = r[0]
        except:sys.exit(0)
        xbmc.executebuiltin("PlayMedia(plugin://plugin.video.youtube/?action=play_video&videoid=%s)"
                            %(trailer_url)[str(trailer_url).rfind("v=")+2:] )            
    
def PlaySource(url, types, meta_name, imdb, iconimage, queued):
    print 'playsource'
    print url
    print types
    print meta_name
    print imdb
    print iconimage
    print queued
    if local.getSetting("enable_meta") == "true":
        if re.findall(r'season\s\d+\sepisode\s\d+',  meta_name, re.I):
            infoLabels = GRABMETA(meta_name, 'episode')
            types = 'tvshow'
            season = infoLabels['season']
            episode= infoLabels['episode']
            whmeta = {'supports_meta': 'true','episode': str(infoLabels['episode']), 'name': meta_name, 'season': str(infoLabels['season']),
                      'video_type': 'Episode', 'imdb_id': infoLabels['imdb_id'], 'cover_url': infoLabels['cover_url']}
            print whmeta
        elif re.findall(r'M.+?HL', imdb):
            infoLabels = GRABMETA(meta_name, 'movie')
            types = 'movie'
            season = ''
            episode= ''
            print infoLabels
            whmeta = {'supports_meta': str('true'),'video_type': str('Movie'), 'imdb_id': str(infoLabels['imdb_id']), 'cover_url': str(infoLabels['cover_url']),
                      'year': str(infoLabels['year']), 'duration': str(infoLabels['duration']), 'title': str(infoLabels['title']), 'fanart': str(infoLabels['backdrop_url']),
                      'cover_url': str(infoLabels['cover_url']), 'imdb_id': str(infoLabels['imdb_id']), 'premiered': str(infoLabels['premiered'])}
        img = infoLabels['cover_url']
        fanart = infoLabels['backdrop_url']
    else:
        fanart = ''
        infoLabels = ''
        img = iconimage
        season = ''
        episode= ''
        whmeta = ''
            
        #print season
        #print episode
    
    if queued:
        pass

    try:
        try:streamlink = urlresolver.resolve(url)
        except:raise Exception ('File Not Found Or Removed')
        wh = watchhistory.WatchHistory(addonID)
        if streamlink:
            if '%3A' in streamlink:
                streamlink = streamlink.replace('%3A', ':').replace('%2F', '/')
            player = playbackengine.PlayWithoutQueueSupport(resolved_url=streamlink, addon_id=addonID, video_type=types, title=meta_name.title(),
                                                            season=season, episode=episode, year='', watch_percent=0.9, watchedCallback='',
                                                            watchedCallbackwithParams=None, imdb_id=None, img=img, fanart=fanart, infolabels=infoLabels)
            print 'img: '+img
            print 'fanart: '+fanart
            wh.add_video_item(str(meta_name).title(), streamlink, infolabels=whmeta, img=img, fanart=fanart, is_playable=True)
            player.KeepAlive()
        else:
            raise Exception ('File Not Found Or Removed')
    except Exception, e:
        xbmc.executebuiltin("XBMC.Notification([COLOR blue]Movie Kingdom Error[/COLOR],[COLOR blue]"+str(e)+"[/COLOR],7000,"+error_logo+")")
        xbmc.log('Movie Kingdom ERROR - No Playable Stream Found: '+str(e))
        sys.exit(0)

def Download(url, types, name, imdb):
    if os.path.exists(downloadPath):
        res_url = []
        res_name = []
        orig_name = name
        orig_imdb = imdb
        hosters = ListHosts(url, name, 'DM')
        for host in hosters:
            name = re.findall(r'\.(\w+)\.', host.title())[0]
            res_url.append(host)
            res_name.append(name)
        dialog = xbmcgui.Dialog()
        ret = dialog.select('Select The Hoster', res_name)
        if ret == -1:return

        url = urlresolver.resolve(res_url[ret])
        if url == False:
            xbmc.executebuiltin("XBMC.Notification([COLOR blue]Movie Kingdom Download Error[/COLOR],[COLOR blue]Unable To Download From This Host Check Log For Details[/COLOR],7000,"+error_logo+")")
            xbmc.log('MOVIEKINGDOM DOWNLOAD ERROR: Unable To Download from '+res_name[ret])
            sys.exit(0)
        else:
            if '%3A' in url:url = url.replace('%3A', ':').replace('%2F', '/')
            if '.flv' in url:name = orig_name+'.flv'
            if '.mkv' in url:name = orig_name+'.mkv'
            if '.avi' in url:name = orig_name+'.avi'
            if '.mp4' in url:name = orig_name+'.mp4'
            else:name = orig_name+'.avi'
            mypath=os.path.join(downloadPath,name)
            if os.path.isfile(mypath) is True:
                xbmc.executebuiltin("XBMC.Notification(Download Alert!,The video you are trying to download already exists!,8000)")
            else:
                DownloadInBack=local.getSetting('download-in-background')
                if DownloadInBack == 'true':
                    QuietDownload(url,mypath,orig_name,name)
                else:
                    DownLoad(url,mypath,orig_name,name)
    else:
        xbmc.executebuiltin("XBMC.Notification(Download Alert!,You have not set the download folder,8000)")
        return False

def QuietDownload(url, dest,originalName, videoname):#thanks goto eldordo from icefilms for this
    #quote parameters passed to download script     
    q_url = urllib.quote_plus(url)
    q_dest = urllib.quote_plus(dest)
    q_vidname = urllib.quote_plus(videoname)
    q_vidOname = urllib.quote_plus(originalName)
    
    #Create possible values for notification
    notifyValues = [2, 5, 10, 20, 25, 50, 100]

    # get notify value from settings
    NotifyPercent=int(local.getSetting('notify-percent'))
    
    script = os.path.join( local.getAddonInfo('path'), 'resources', 'lib', "DownloadInBackground.py" )
    xbmc.executebuiltin( "RunScript(%s, %s, %s, %s, %s, %s)" % ( script, q_url, q_dest, q_vidname,q_vidOname, str(notifyValues[NotifyPercent]) ) )
    return True


def DownLoad(url, dest,originalName, displayname=False):
         
        if displayname == False:
            displayname=url
        delete_incomplete = 'true'
        dp = xbmcgui.DialogProgress()
        dp.create('Downloading:    '+displayname)
        start_time = time.time() 
        try: 
            urllib.urlretrieve(url, dest, lambda nb, bs, fs: _pbhook(nb, bs, fs, dp, start_time))
            open(DownloadFile,'a').write('{name="%s",destination="%s"}'%(originalName,dest))
            
        except:
            if delete_incomplete == 'true':
                #delete partially downloaded file if setting says to.
                while os.path.exists(dest): 
                    try: 
                        os.remove(dest) 
                        break 
                    except: 
                        pass 
            #only handle StopDownloading (from cancel), ContentTooShort (from urlretrieve), and OS (from the race condition); let other exceptions bubble 
            if sys.exc_info()[0] in (urllib.ContentTooShortError, StopDownloading, OSError): 
                return False 
            else: 
                raise 
            return False
        return True

def _pbhook(numblocks, blocksize, filesize, dp, start_time):
        try: 
            percent = min(numblocks * blocksize * 100 / filesize, 100) 
            currently_downloaded = float(numblocks) * blocksize / (1024 * 1024) 
            kbps_speed = numblocks * blocksize / (time.time() - start_time) 
            if kbps_speed > 0: 
                eta = (filesize - numblocks * blocksize) / kbps_speed 
            else: 
                eta = 0 
            kbps_speed = kbps_speed / 1024 
            total = float(filesize) / (1024 * 1024) 
            mbs = '%.02f MB of %.02f MB' % (currently_downloaded, total) 
            e = 'Speed: %.02f Kb/s ' % kbps_speed 
            e += 'ETA: %02d:%02d' % divmod(eta, 60) 
            dp.update(percent, mbs, e)
        except: 
            percent = 100 
            dp.update(percent) 
        if dp.iscanceled(): 
            dp.close() 
            raise StopDownloading('Stopped Downloading')


    
def OpenUrl(url):
    try:
        html = net(user_agent=userAgent).http_GET(url).content
        #import HTMLParser
        #h = HTMLParser.HTMLParser()
        #html = h.unescape(html)
        return html#.encode('utf-8')
    except urllib2.URLError, e:
        xbmc.executebuiltin("XBMC.Notification([COLOR blue]Movie Kingdom Network Error[/COLOR],[COLOR blue]Failed To Connect To MovieKingdom.com Check Log For Details[/COLOR],7000,"+error_logo+")")
        xbmc.log('MOVIEKINGDOM NETWORK ERROR: '+str(e))
        sys.exit(0)
        
    

def setView(content, viewType):
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if addon.get_setting('auto-view') == 'true':
        xbmc.executebuiltin("Container.SetViewMode(%s)" % addon.get_setting(viewType) )
        
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RATING )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_PROGRAM_COUNT )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_VIDEO_RUNTIME )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_GENRE )

def GRABMETA(meta_name,types):
    print types
    print meta_name
    type = types
    if type == None: meta = {'cover_url': '','title': name}
    if type == 'movie':
        meta = grab.get_meta('movie', meta_name, '', '', '', overlay=6)
        print meta

        
    if type == 'episode':
        r = re.findall(r'(.+?):\s\w+\s(\d+)\s\w+\s(\d+)', meta_name.strip(), re.I)
        for name, season, episode in r:
            meta = grab.get_meta('tvshow', name, '', '', '', overlay=6)
            imdb = meta['imdb_id']
            meta = grab.get_episode_meta(name, imdb, season, episode, air_date='', episode_title='', overlay='')
            if meta['cover_url'] == '':
                t = grab.get_meta('tvshow', name, '', '', '', overlay=6)
                meta['cover_url'] = t['banner_url']
                
    if type == 'tvshow':
        meta = grab.get_meta('tvshow', meta_name, '', '', '', overlay=6)

    if type == 'season':
        r = re.findall(r'\/show\/(.+?)\/season\/(\d+)', meta_name, re.I)
        for name, season in r:
            t = grab.get_meta('tvshow', name, '', '', '', overlay=6)
            imdb = t['imdb_id']
            r = grab.get_seasons(name, imdb, season)
            r = str(r).replace("u'", "'")
            r = re.findall(r'cover_url\':\s\'(.+?)\'.+?backdrop_url\':\s\'(.+?)\'', str(r))
            for seasons, backdrop in r:
                meta = {'cover_url': seasons, 'title': name, 'backdrop_url': backdrop, 'TVShowTitle': t['TVShowTitle'], 'year': t['year'],
                        'plot': t['plot'], 'mpaa': t['mpaa'], 'status': t['status'], 'genre': t['genre'], 'premiered': t['premiered'], 'rating': t['rating'] }
                
    return meta


class StopDownloading(Exception): 
    def __init__(self, value):
        self.value = value 
        def __str__(self): 
            return repr(self.value)

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

def addDir(mode,url,types,meta_name,name,iconimage,totalItems,imdb,special,queued):
    img = iconimage
    u   = sys.argv[0]
    u  += "?mode="          + str(mode)
    u  += "&url="           + str(url)
    u  += "&types="         + str(types)
    u  += "&meta_name="     + str(meta_name)
    u  += "&name="          + str(name)
    u  += "&iconimage="     + str(iconimage)
    u  += "&totalItems="    + str(totalItems)
    u  += "&imdb="          + str(imdb)
    u  += "&special="       + str(special)
    u  += "&queued="        + str(queued)


    if local.getSetting("enable_meta") == "true" and types != None:
        infoLabels = GRABMETA(meta_name,types)
    else:infoLabels = {'cover_url': img, 'title': name}
    if types == None:img = iconimage
    else: img = infoLabels['cover_url']
    ok  = True
    liz = xbmcgui.ListItem(name, iconImage = "DefaultFolder.png", thumbnailImage=img)
        
    ContextMenuItems = []
    ContextMenuItems.append(('Resolver Settings', 'XBMC.RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0], 300, url)))
    ContextMenuItems.append(('Addon Settings', 'XBMC.RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0], 310, url)))
    ContextMenuItems.append(('Favorites Settings', 'XBMC.RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0], 320, url)))
    ContextMenuItems.append(('MetaHandler Settings', 'XBMC.RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0], 330, url)))
    
    if re.findall('MV', imdb) and types != None:
        ContextMenuItems.insert(0,('Watch Trailer', 'XBMC.RunPlugin(%s?mode=%s&url=%s)' % (sys.argv[0],60,url)))
        
    if types != None:
        ContextMenuItems.insert(1,('Download', 'XBMC.RunPlugin(%s?mode=%s&url=%s&types=%s&name=%s&imdb=%s)' % (sys.argv[0], 70, url, types, name, imdb)))

        if local.getSetting("enable_meta") == "true":
            infoL = infoLabels
            img = infoLabels['cover_url']
            fanart = infoLabels['backdrop_url']
            if types == 'episode':types = 'tv shows'
        else:
            infoL = ''
            img = iconimage
            fanart = ''
            if types == 'episode':types = 'tv shows'
        plugin_url = sys.argv[0]+'?mode=20&url='+url+'&name='+name+'&types='+types+'&imdb='+imdb
        ContextMenuItems.insert(2,('Add to Favorites', fav.add_directory(name, plugin_url, section_title=types.title(), infolabels=infoL,
                                                                         img=img, fanart=fanart)))


    
    liz.addContextMenuItems((ContextMenuItems), replaceItems=True)
    #if types == None:
    #liz.addContextMenuItems(ContextMenuItems)


    try: liz.setProperty('fanart_image', infoLabels['backdrop_url'])
    except: pass

    liz.setInfo( type="Video", infoLabels=infoLabels)
    if special == True: ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False,totalItems=int(totalItems))
    else: ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True,totalItems=int(totalItems))
    return ok

params      = get_params()
mode        = None
url         = None
types       = None
meta_name   = None
name        = None
iconimage   = None
totalItems  = None
imdb        = None
special     = None
queued      = None


try:    mode        = int(params["mode"])
except: pass
try:    url         = urllib.unquote_plus(params["url"])
except: pass
try:    types       = urllib.unquote_plus(params["types"])
except: pass
try:    meta_name   = urllib.unquote_plus(params["meta_name"])
except: pass
try:    name        = urllib.unquote_plus(params["name"])
except: pass
try:    iconimage   = urllib.unquote_plus(params["iconimage"])
except: pass
try:    totalItems  = int(params["totalItems"])
except: pass
try:    imdb        = urllib.unquote_plus(params["imdb"])
except: pass
try:    special     = urllib.unquote_plus(params["special"])
except: pass
try:    queued      = params["queued"]
except: pass

xbmc.log('======================================================')
xbmc.log('Mode: '.title() +str(mode))
xbmc.log('Url: '.title() +str(url))
xbmc.log('meta_name: '.title() +str(meta_name))
xbmc.log('name: '.title() +str(name))
xbmc.log('iconimage: '.title() +str(iconimage))
xbmc.log('totalItems: '.title() +str(totalItems))
xbmc.log('imdb: '.title() +str(imdb))
xbmc.log('special: '.title() +str(special))
xbmc.log('queued: '.title() +str(queued))
xbmc.log('======================================================')

if mode==None or url==None or len(url)<1:
    MAIN()
    setView('default', 'default')

elif mode == 10:
    TvEpisodes(url, imdb)
    setView('episodes', 'episode')

elif mode == 11:
    if imdb == 'TVR':
        content = 'tvshows'
        viewtype = 'tvshow'
    elif imdb == 'MVR':
        content = 'movies'
        viewtype = 'movie'
    Random(url, imdb)
    setView(content, viewtype)
    

elif mode == 13:
    TvSeason(url, meta_name, imdb)
    setView('tvshows', 'season')
    
elif mode == 14:
    if imdb == 'TVG':
        content = 'tvshows'
        viewtype = 'tvshow'
    elif imdb == 'MVG':
        content = 'movies'
        viewtype = 'movie'
    Genre(url, imdb)
    setView(content, viewtype)

elif mode == 15:
    if imdb == 'TVA':
        content = 'tvshows'
        viewtype = 'tvshow'
    if imdb == 'MVZ':
        content = 'movies'
        viewtype = 'movie'
    AtoZ(url, imdb)
    setView(content, viewtype)

elif mode == 20:
    ListHosts(url, name, imdb)

elif mode == 30:
    MoviesLatest(url, imdb)
    setView('movies', 'movie')

elif mode == 40:
    MusicIndex(url, imdb)

elif mode == 60:
    WatchTrailer(url)

elif mode == 70:
    Download(url, types, name, imdb)


elif mode == 100:
    PlaySource(url, types, meta_name, imdb, iconimage, queued)

elif mode == 200:
    Search(url, imdb)

elif mode == 300:
    urlresolver.display_settings()

elif mode == 310:
    addon.show_settings()

elif mode == 320:
    from universal import _common
    _common.addon.show_settings()

elif mode == 330:
    import metahandler
    metahandler.display_settings()
    




xbmcplugin.endOfDirectory(int(sys.argv[1]),succeeded=True)
