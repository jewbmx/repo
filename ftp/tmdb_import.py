
### Info: In this file ive added about everything i can think of that ya might need to go with the tmdb module.

## settings.xml
"""

        <setting type="lsep" label="TMDb" />
        <setting id="tmdb.api" type="text" option="hidden" label="API:" default="" />
        <setting id="tmdb.user" type="text" label="Username:" default="" />
        <setting id="tmdb.pass" type="text" option="hidden" label="Password:" default="" />
        <setting id="tmdb.session" type="text" label="Account Session:" default="" enable="false" visible="true" />
        <setting id="tmdb.id" type="text" label="Account ID:" default="" enable="false" visible="true" />

"""
## main.py
"""

elif action == 'shitTesting':
    #from resources.lib.modules import tmdb
    #tmdb.get_created_lists()
    movies.movies().shit_testing()

elif action == 'authTMDb':
    from resources.lib.modules import tmdb
    tmdb.authTMDb()

"""
## navigator.py
"""

self.addDirectoryItem('Authorize TMDb', 'authTMDb', 'tmdb.png', 'DefaultAddonProgram.png', isFolder=False)
self.addDirectoryItem('Shit Testing', 'shitTesting', 'tools.png', 'DefaultSets.png')
self.addDirectoryItem('Link Testing', 'movies&url=tmdb_in_theatres', 'tools.png', 'DefaultMovies.png')
self.addDirectoryItem('TMDb Favorites', 'movies&url=tmdb_favorites', 'mymovies.png', 'DefaultMovies.png')
self.addDirectoryItem('TMDb Watchlist', 'movies&url=tmdb_watchlist', 'mymovies.png', 'DefaultMovies.png')
self.addDirectoryItem('Movie Lists', 'movieUserlists', 'mymovies.png', 'DefaultMovies.png')

"""
## movies.py
"""

from resources.lib.modules import tmdb

    def __init__(self):
        self.list = []

        self.trakt_link = 'https://api.trakt.tv'
        self.imdb_link = 'https://www.imdb.com'
        self.tmdb_link = 'https://api.themoviedb.org'

        self.tmdb_key = control.setting('tmdb.api')
        if self.tmdb_key == '' or self.tmdb_key == None:
            self.tmdb_key = base64.b64decode('<<API>>')
        self.tmdb_session = control.setting('tmdb.session')

        self.tmdb_info_link = self.tmdb_link + '/3/movie/%s?api_key=%s&language=en-US&append_to_response=credits,releases' % ('%s', self.tmdb_key)
        self.tmdb_by_query_imdb_link = self.tmdb_link + '/3/find/%s?api_key=%s&external_source=imdb_id' % ('%s', self.tmdb_key)
        self.tmdb_image_link = 'https://image.tmdb.org/t/p/original'

        self.tmdb_in_theatres_link = self.tmdb_link + '/3/discover/movie?api_key=%s&release_date.gte=date[90]&release_date.lte=date[0]&language=en-US&page=1' % self.tmdb_key
        self.tmdb_userlists_link = self.tmdb_link + '/3/list/%s?api_key=%s&language=en-US&page=1' % ('%s', self.tmdb_key)
        self.tmdb_jewtestmovies_link = self.tmdb_userlists_link % ('97123')

        self.tmdb_favorites_link = tmdb.get_movie_favorites()
        self.tmdb_watchlist_link = tmdb.get_movie_watchlist()
        # with my testing these 2 links being ran without auth just opens to a blank so the else was a waste of time.


    def shit_testing(self):
        try:
            #url = self.tmdb_info_link % '9600'
            #test = client.scrapePage(url).json()

            from resources.lib.modules import tmdb
            test = tmdb.get_movie_account_states(9600)

            log_utils.log('shit_testing - test: ' + repr(test))
            self.addDirectory(self.list)
            return self.list
        except:
            log_utils.log('shit_testing', 1)
            return self.list


    def userlists(self):
        #
        try:
            self.list = []
            from resources.lib.modules import tmdb
            userlists += cache.get(tmdb.get_created_lists, 0, self.tmdb_userlists_link)
        except:
            pass
        #


    def get(self, url, idx=True, create_directory=True):
        try:
            try:
                url = getattr(self, url + '_link')
            except:
                pass
            try:
                u = urllib_parse.urlparse(url).netloc.lower()
            except:
                pass
            if u in self.tmdb_link and ('/list/' in url or '/collection/' in url):
                self.list = cache.get(self.tmdb_list, 24, url)
                self.list = sorted(self.list, key=lambda k: k['year'])
                if idx == True:
                    self.worker()
            elif u in self.tmdb_link and self.tmdb_search_link in url:
                self.list = cache.get(self.tmdb_list, 1, url)
                if idx == True:
                    self.worker()
            elif u in self.tmdb_link:
                self.list = cache.get(self.tmdb_list, 24, url)
                if idx == True:
                    self.worker()
            #


    def tmdb_list(self, url):
        try:
            next = url
            if 'date[' in url:
                for i in re.findall('date\[(\d+)\]', url):
                    url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days=int(i))).strftime('%Y-%m-%d'))
            result = client.scrapePage(url).json()
            try:
                page = int(result['page'])
                total = int(result['total_pages'])
                if page >= total:
                    raise Exception()
                if not 'page=' in url:
                    raise Exception()
                next = '%s&page=%s' % (next.split('&page=', 1)[0], str(page+1))
            except:
                next = ''
            if 'results' in result:
                items = result['results']
            elif 'items' in result:
                items = result['items']
            elif 'parts' in result:
                items = result['parts']
            for item in items:
                try:
                    if 'media_type' in item and not item['media_type'] == 'movie':
                        raise Exception()
                    title = item['title']
                    title = client.replaceHTMLCodes(title)
                    originaltitle = item['original_title']
                    originaltitle = client.replaceHTMLCodes(originaltitle)
                    year = item['release_date']
                    year = re.compile('(\d{4})').findall(year)[0]
                    if int(year) > int((self.datetime).strftime('%Y')): raise Exception()
                    tmdb = item['id']
                    tmdb = re.sub('[^0-9]', '', str(tmdb))
                    self.list.append({'title': title, 'originaltitle': originaltitle, 'year': year, 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'next': next})
                except:
                    pass
        except:
            pass
        return self.list


"""


