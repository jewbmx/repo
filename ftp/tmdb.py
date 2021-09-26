# -*- coding: utf-8 -*-

import requests
from requests.compat import json, str

from resources.lib.modules import control
from resources.lib.modules import log_utils


USERNAME = control.setting('tmdb.user')
PASSWORD = control.setting('tmdb.pass')
SESSION_ID = control.setting('tmdb.session')
ACCOUNT_ID = control.setting('tmdb.id')

API_KEY = control.setting('tmdb.api')
if not API_KEY:
    API_KEY = '<<API>>'

API_URL = 'https://api.themoviedb.org/3/'
HEADERS = {'Content-Type': 'application/json;charset=utf-8'}


############################################
############################################


def authTMDb():
    try:
        if not SESSION_ID == '':
            if control.yesnoDialog('A Session Already Exists.' + '[CR]' + 'Delete Session?', heading='TMDB'):
                return delete_session()
            raise Exception()
        if USERNAME == '' or PASSWORD == '':
            control.infoDialog('Check Account Credentials.', sound=True)
            raise Exception()
        request_token = create_request_token()
        if not request_token:
            raise Exception()
        request_token = create_session_with_login(request_token)
        if not request_token:
            raise Exception()
        session_id = create_session(request_token)
        if not session_id:
            raise Exception()
        control.setSetting(id='tmdb.session', value=session_id)
        control.infoDialog('TMDb Auth Successful.', sound=True)
        return get_account_details(session_id)
    except:
        log_utils.log('authTMDb', 1)
        control.infoDialog('TMDb Auth Failed.', sound=True)
        return


############################################
############################################


def create_request_token():
    try:
        url = API_URL + 'authentication/token/new?api_key=%s' % API_KEY
        result = requests.get(url, headers=HEADERS).json()
        if not result.get('success') is True:
            raise Exception()
        request_token = result['request_token']
        return request_token
    except:
        log_utils.log('create_request_token', 1)
        return None


############################################
############################################


def create_session_with_login(request_token):
    try:
        url = API_URL + 'authentication/token/validate_with_login?api_key=%s' % API_KEY
        post = {"username": "%s" % str(USERNAME), "password": "%s" % str(PASSWORD), "request_token": "%s" % str(request_token)}
        result = requests.post(url, data=json.dumps(post), headers=HEADERS).json()
        if not result.get('success') is True:
            raise Exception()
        request_token = result['request_token']
        return request_token
    except:
        log_utils.log('create_session_with_login', 1)
        return None


############################################
############################################


def create_session(request_token):
    try:
        url = API_URL + 'authentication/session/new?api_key=%s' % API_KEY
        post = {"request_token": "%s" % str(request_token)}
        result = requests.post(url, data=json.dumps(post), headers=HEADERS).json()
        if not result.get('success') is True:
            raise Exception()
        session_id = result['session_id']
        return session_id
    except:
        log_utils.log('create_session', 1)
        return None


############################################
############################################


def delete_session():
    try:
        if SESSION_ID == '':
            raise Exception()
        url = API_URL + 'authentication/session?api_key=%s' % API_KEY
        post = {"session_id": "%s" % str(SESSION_ID)}
        result = requests.delete(url, data=json.dumps(post), headers=HEADERS).json()
        if not result.get('success') is True:
            raise Exception()
        control.setSetting(id='tmdb.session', value='')
        if not ACCOUNT_ID == '':
            control.setSetting(id='tmdb.id', value='')
        control.infoDialog('TMDb delete_session Successful', sound=True)
    except:
        control.infoDialog('TMDb delete_session Failed', sound=True)
        log_utils.log('delete_session', 1)
        pass


############################################
############################################


def get_account_details(session_id):
    try:
        url = API_URL + 'account?api_key=%s&session_id=%s' % (API_KEY, session_id)
        result = requests.get(url, headers=HEADERS).json()
        account_username = result['username']
        account_name = result['name']
        account_id = result['id']
        account_include_adult = result['include_adult']
        account_iso_639_1 = result['iso_639_1']
        account_iso_3166_1 = result['iso_3166_1']
        control.setSetting(id='tmdb.id', value=str(account_id))
        message = ('username: %s' % str(account_username) + '[CR]' + 'name: %s' % str(account_name) + '[CR]' + 'id: %s' % str(account_id) + '[CR]' + 'include_adult: %s' % str(account_include_adult) + '[CR]' + 'iso_639_1: %s' % str(account_iso_639_1) + '[CR]' + 'iso_3166_1: %s' % str(account_iso_3166_1))
        return control.okDialog(message, heading='TMDB Account Details')
    except:
        log_utils.log('get_account_details', 1)
        pass


############################################
############################################


def get_created_lists(url):
    try:
        lists_url = API_URL + 'account/%s/lists?api_key=%s&language=en-US&session_id=%s&page=1' % (ACCOUNT_ID, API_KEY, SESSION_ID)
        result = requests.get(lists_url, headers=HEADERS).json()
        try:
            page = int(result['page'])
            total = int(result['total_pages'])
            if page >= total:
                raise Exception()
            if not 'page=' in lists_url:
                raise Exception()
            next = '%s&page=%s' % (lists_url.split('&page=', 1)[0], str(page+1))
        except:
            next = ''
        items = []
        lists = result['results']
        for list in lists:
            list_name = list['name']
            list_id = list['id']
            list_url = url % list_id
            items.append({'name': list_name, 'url': list_url, 'context': list_url, 'image': 'tmdb.png', 'next': next})
        return items
    except:
        log_utils.log('get_created_lists', 1)
        return items


############################################
############################################


def mark_as_favorite(tmdb, media_type):
    try:
        url = API_URL + 'account/%s/favorite?api_key=%s&session_id=%s' % (ACCOUNT_ID, API_KEY, SESSION_ID)
        post = {
            "media_type": "%s" % str(media_type),
            "media_id": "%s" % str(tmdb),
            "favorite": "true"
        }
        result = requests.post(url, data=json.dumps(post), headers=HEADERS).json()
        status_code = result['status_code']
        status_message = result['status_message']
        return {'status_code': status_code, 'status_message': status_message}
    except:
        log_utils.log('mark_as_favorite', 1)
        return {'status_code': None, 'status_message': None}


############################################
############################################


def add_to_watchlist(tmdb, media_type):
    try:
        url = API_URL + 'account/%s/watchlist?api_key=%s&session_id=%s' % (ACCOUNT_ID, API_KEY, SESSION_ID)
        post = {
            "media_type": "%s" % str(media_type),
            "media_id": "%s" % str(tmdb),
            "watchlist": "true"
        }
        result = requests.post(url, data=json.dumps(post), headers=HEADERS).json()
        status_code = result['status_code']
        status_message = result['status_message']
        return {'status_code': status_code, 'status_message': status_message}
    except:
        log_utils.log('add_to_watchlist', 1)
        return {'status_code': None, 'status_message': None}


############################################
############################################


def get_movie_account_states(tmdb):
    try:
        url = API_URL + 'movie/%s/account_states?api_key=%s&session_id=%s' % (tmdb, API_KEY, SESSION_ID)
        result = requests.get(url, headers=HEADERS).json()
        favorite = result['favorite']
        watchlist = result['watchlist']
        return {'favorite': favorite, 'watchlist': watchlist}
    except:
        log_utils.log('get_movie_account_states', 1)
        return {'favorite': None, 'watchlist': None}


############################################
############################################


def get_trailers(tmdb):
    try:
        list = []
        url = API_URL + 'movie/%s/videos?api_key=%s&language=en-US' % (tmdb, API_KEY)
        result = requests.get(url, headers=HEADERS).json()
        items = result['results']
        for item in items:
            list.append(item)
        return list
    except:
        log_utils.log('get_trailers', 1)
        return list


############################################
############################################


#Get Favorite Movies
#get/account/{account_id}/favorite/movies

#Get the list of your favorite movies.


#https://api.themoviedb.org/3/account/{account_id}/favorite/movies?api_key=<<api_key>>&session_id=<session_id>&language=en-US&page=1
#https://api.themoviedb.org/3/account/{account_id}/favorite/movies?api_key=<<api_key>>&session_id=<session_id>&language=en-US&sort_by=created_at.asc&page=1
#https://api.themoviedb.org/3/account/{account_id}/favorite/movies?api_key=<<api_key>>&session_id=<session_id>&language=en-US&sort_by=created_at.desc&page=1


#Responses application/json
#{
  #"page": 1,
  #"results": [
    #{
      #"adult": false,
      #"backdrop_path": null,
      #"genre_ids": [
        #16
      #],
      #"id": 9806,
      #"original_language": "en",
      #"original_title": "The Incredibles",
      #"overview": "PLOT",
      #"release_date": "2004-11-04",
      #"poster_path": null,
      #"popularity": 0.167525,
      #"title": "The Incredibles",
      #"video": false,
      #"vote_average": 6.8,
      #"vote_count": 1584
    #}
  #],
  #"total_pages": 4,
  #"total_results": 77
#}


def get_movie_favorites():
    try:
        url = API_URL + 'account/%s/favorite/movies?api_key=%s&session_id=%s&language=en-US&page=1' % (ACCOUNT_ID, API_KEY, SESSION_ID)
        return url
    except:
        log_utils.log('get_movie_favorites', 1)
        return


############################################
############################################


#Get Favorite TV Shows
#get/account/{account_id}/favorite/tv

#Get the list of your favorite TV shows.


#https://api.themoviedb.org/3/account/{account_id}/favorite/tv?api_key=<<api_key>>&session_id=<session_id>&language=en-US&page=1
#https://api.themoviedb.org/3/account/{account_id}/favorite/tv?api_key=<<api_key>>&session_id=<session_id>&language=en-US&sort_by=created_at.asc&page=1
#https://api.themoviedb.org/3/account/{account_id}/favorite/tv?api_key=<<api_key>>&session_id=<session_id>&language=en-US&sort_by=created_at.desc&page=1


#Responses application/json
#{
  #"page": 1,
  #"results": [
    #{
      #"backdrop_path": null,
      #"first_air_date": "2007-09-24",
      #"genre_ids": [
        #10759
      #],
      #"id": 1404,
      #"original_language": "en",
      #"original_name": "Chuck",
      #"overview": "PLOT",
      #"origin_country": [
        #"US"
      #],
      #"poster_path": null,
      #"popularity": 0.125125,
      #"name": "Chuck",
      #"vote_average": 8.2,
      #"vote_count": 37
    #}
  #],
  #"total_pages": 3,
  #"total_results": 52
#}


############################################
############################################


#Get Movie Watchlist
#get/account/{account_id}/watchlist/movies

#Get a list of all the movies you have added to your watchlist.


#https://api.themoviedb.org/3/account/{account_id}/watchlist/movies?api_key=<<api_key>>&language=en-US&session_id=<session_id>&sort_by=created_at.asc&page=1


#Responses application/json
#{
  #"page": 1,
  #"results": [
    #{
      #"adult": false,
      #"backdrop_path": null,
      #"genre_ids": [
        #18
      #],
      #"id": 76726,
      #"original_language": "it",
      #"original_title": "Chronicle",
      #"overview": "PLOT",
      #"release_date": "2012-02-02",
      #"poster_path": null,
      #"popularity": 0.237951,
      #"title": "Chronicle",
      #"video": false,
      #"vote_average": 6.2,
      #"vote_count": 545
    #}
  #],
  #"total_pages": 14,
  #"total_results": 277
#}


def get_movie_watchlist():
    try:
        url = API_URL + 'account/%s/watchlist/movies?api_key=%s&session_id=%s&language=en-US&page=1' % (ACCOUNT_ID, API_KEY, SESSION_ID)
        return url
    except:
        log_utils.log('get_movie_watchlist', 1)
        return


############################################
############################################


#Get TV Show Watchlist
#get/account/{account_id}/watchlist/tv

#Get a list of all the TV shows you have added to your watchlist.


#https://api.themoviedb.org/3/account/{account_id}/watchlist/tv?api_key=<<api_key>>&language=en-US&session_id=<session_id>&sort_by=created_at.asc&page=1


#Responses application/json
#{
  #"page": 1,
  #"results": [
    #{
      #"backdrop_path": null,
      #"first_air_date": "2013-09-26",
      #"genre_ids": [
        #35
      #],
      #"id": 58932,
      #"original_language": "en",
      #"original_name": "The Crazy Ones",
      #"overview": "PLOT",
      #"origin_country": [
        #"US"
      #],
      #"poster_path": null,
      #"popularity": 0.075407,
      #"name": "The Crazy Ones",
      #"vote_average": 5.3,
      #"vote_count": 4
    #}
  #],
  #"total_pages": 4,
  #"total_results": 64
#}


