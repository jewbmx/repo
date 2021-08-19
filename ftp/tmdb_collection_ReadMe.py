


'''


####
    The file 'tmdb_collection_ids.json' is a modified version of the daily exports file TMDb does.
    I added a little extra info to my version for simple checking plus ease of access that matches my OCD.
    Examples for everything should be included here that i was doing in the movies.py Indexer for Scrubs.
    Slight changes are likely needed in multiple areas in order to use any of this stuff.
    Best use for the .json file is to go thru it by hand and create your own lists and ditch the trash.

    Note that in my tests of def tmdb_collections_testing2 i found that most the collections are poorly done.
    UserLists links are probably still a better option in most cases compared to these collections links.
####


########## The Various TMDb Daily Exports File Choices.


## Keywords
# http://files.tmdb.org/p/exports/keyword_ids_MM_DD_YYYY.json.gz

## TV Networks
# http://files.tmdb.org/p/exports/tv_network_ids_MM_DD_YYYY.json.gz

## Production Companies
# http://files.tmdb.org/p/exports/production_company_ids_MM_DD_YYYY.json.gz

## Collections
# http://files.tmdb.org/p/exports/collection_ids_03_16_2018.json.gz


#######################################################


########## The Various TMDb Crap For The Movies Indexer.


        self.tmdb_collections_link = 'https://api.themoviedb.org/3/collection/%s?api_key=%s&language=en-US' % ('%s', self.tmdb_key)


    def tmdb_collections_testing1(self):
        try:
            url = 'https://raw.githubusercontent.com/jewbmx/repo/master/ftp/tmdb_collection_ids.json'
            result = client.scrapePage(url).json()
            items = result['collections']
            for item in items:
                collection_id = item['id']
                collection_name = item['name']
                collection_name = client.replaceHTMLCodes(collection_name)
                self.list.append({'name': collection_name, 'url': self.tmdb_collections_link % collection_id, 'image': 'tmdb.png', 'action': 'movies'})
            self.addDirectory(self.list)
            return self.list
        except:
            log_utils.log('shit_testing', 1)
            return self.list


    def tmdb_collections_testing2(self):
        collections = [
            ('Back to the Future Collection', '264'),
            ('Blade Collection', '735'),
            ('Die Hard Collection', '1570'),
            ('Indiana Jones Collection', '84'),
            ('James Bond Collection', '645'),
            ('Lethal Weapon Collection', '945'),
            ('Oceans Collection', '304'),
            ('Planet of the Apes (Original) Collection', '1709'),
            ('Rocky Collection', '1575'),
            ('Shaft Collection', '495'),
            ('Spider-Man Collection', '556'),
            ('Star Trek: The Original Series Collection', '151'),
            ('Star Wars Collection', '10'),
            ('Teenage Mutant Ninja Turtles Collection', '1582'),
            ('The Dark Knight Collection', '263'),
            ('The Mummy Collection', '1733'),
            ('The Terminator Collection', '528'),
            ('X-Men Collection', '748'),
            ('Zorro Collection', '1657')
        ]
        for collection in collections:
            self.list.append({'name': collection[0], 'url': self.tmdb_collections_link % collection[1], 'image': 'tmdb.png', 'action': 'movies'})
        self.addDirectory(self.list)
        return self.list


    def tmdb_clean_genres(self, genre_id):
        genres = [
            {'id': 28, 'name': 'Action'},
            {'id': 12, 'name': 'Adventure'},
            {'id': 16, 'name': 'Animation'},
            {'id': 35, 'name': 'Comedy'},
            {'id': 80, 'name': 'Crime'},
            {'id': 99, 'name': 'Documentary'},
            {'id': 18, 'name': 'Drama'},
            {'id': 10751, 'name': 'Family'},
            {'id': 14, 'name': 'Fantasy'},
            {'id': 36, 'name': 'History'},
            {'id': 27, 'name': 'Horror'},
            {'id': 10402, 'name': 'Music'},
            {'id': 9648, 'name': 'Mystery'},
            {'id': 10749, 'name': 'Romance'},
            {'id': 878, 'name': 'Science Fiction'},
            {'id': 10770, 'name': 'TV Movie'},
            {'id': 53, 'name': 'Thriller'},
            {'id': 10752, 'name': 'War'},
            {'id': 37, 'name': 'Western'}
        ]
        for genre in genres:
            id = genre['id']
            name = genre['name']
            if genre_id == id:
                return name
        return


    def tmdb_list(self, url):
        next = url
        if 'date[' in url:
            for i in re.findall('date\[(\d+)\]', url):
                url = url.replace('date[%s]' % i, (self.datetime - datetime.timedelta(days=int(i))).strftime('%Y-%m-%d'))
        result = client.scrapePage(url).json()
        try:
            items = result['results']
        except:
            try:
                items = result['items']
            except:
                items = result['parts']
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total:
                raise Exception()
            url2 = '%s&page=%s' % (url.split('&page=', 1)[0], str(page+1))
            result = client.scrapePage(url2).json()
            items += result['results']
        except:
            pass
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
        for item in items:
            try:
                try:
                    media_type = item['media_type']
                    if not media_type == 'movie':
                        raise Exception()
                except:
                    pass
                title = item['title']
                title = client.replaceHTMLCodes(title)
                originaltitle = item['original_title']
                originaltitle = client.replaceHTMLCodes(originaltitle)
                year = item['release_date']
                year = re.compile('(\d{4})').findall(year)[-1]
                tmdb = item['id']
                tmdb = re.sub('[^0-9]', '', str(tmdb))
                poster = item['poster_path']
                if poster == '' or poster == None:
                    poster = '0'
                if not poster == '0':
                    poster = self.tmdb_poster + poster
                fanart = item['backdrop_path']
                if fanart == '' or fanart == None:
                    fanart = '0'
                if not fanart == '0':
                    fanart = self.tmdb_image + fanart
                premiered = item['release_date']
                try:
                    premiered = re.compile('(\d{4}-\d{2}-\d{2})').findall(premiered)[0]
                except:
                    premiered = '0'
                rating = str(item['vote_average'])
                if rating == '' or rating == None:
                    rating = '0'
                votes = str(item['vote_count'])
                try:
                    votes = str(format(int(votes), ',d'))
                except:
                    pass
                if votes == '' or votes == None:
                    votes = '0'
                plot = item['overview']
                if plot == '' or plot == None:
                    plot = '0'
                plot = client.replaceHTMLCodes(plot)
                tagline = re.compile('[.!?][\s]{1,2}(?=[A-Z])').split(plot)[0]
                genre = item['genre_ids']
                if genre:
                    genre = [self.tmdb_clean_genres(i) for i in genre]
                    genre = ' / '.join(genre)
                else:
                    genre = '0'
                self.list.append({'title': title, 'originaltitle': originaltitle, 'year': year, 'premiered': premiered, 'studio': '0', 'genre': genre, 'duration': '0', 'rating': rating, 'votes': votes, 'mpaa': '0',
                    'director': '0', 'writer': '0', 'cast': '0', 'plot': plot, 'tagline': tagline, 'code': '0', 'imdb': '0', 'tmdb': tmdb, 'tvdb': '0', 'poster': poster, 'banner': '0', 'fanart': fanart, 'next': next}
                )
            except:
                pass
        return self.list


#######################################################


'''


