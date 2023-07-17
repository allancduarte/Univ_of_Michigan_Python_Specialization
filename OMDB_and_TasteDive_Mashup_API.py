# Process of mashing up data from two different APIs to make movie recommendations.
# The TasteDive API lets you provide a movie (or bands, TV shows, etc.) as a query input,
# and returns a set of related items. The OMDB API lets you provide a movie title as a query
# input and get back data about the movie, including scores from various review sites (Rotten Tomatoes, IMDB, etc.).
# You will put those two together. You will use TasteDive to get related movies for a whole list of titles.
# You’ll combine the resulting lists of related movies, and sort them according to their Rotten Tomatoes scores
# (which will require making API calls to the OMDB API.)
# Your first task will be to fetch data from TasteDive. The documentation for the API is at
# https://tastedive.com/read/api.
# Define a function, called get_movies_from_tastedive. It should take one input parameter,
# a string that is the name of a movie or music artist. The function should return the 5 TasteDive
# results that are associated with that string; be sure to only get movies, not other kinds of media.
# It will be a python dictionary with just one key, ‘Similar’.

import requests_with_caching
import json


def get_movies_from_tastedive(movie):
    par = {}
    par['q'] = movie
    par['type'] = 'movies'
    par['limit'] = '5'
    url = 'https://tastedive.com/api/similar'
    results = requests_with_caching.get(url, params=par)
    tastedive_movies = json.loads(results.text)
    return tastedive_movies


# Next, you will need to write a function that extracts just the list of movie titles from a dictionary returned
# by get_movies_from_tastedive. Call it extract_movie_titles.

def extract_movie_titles(dic):
    taste_dic = dic
    taste_extracted_movies = [name['Name'] for name in taste_dic['Similar']['Results']]
    return taste_extracted_movies

# Next, you’ll write a function, called get_related_titles. It takes a list of movie titles as input.
# It gets five related movies for each from TasteDive, extracts the titles for all of them, and combines
# them all into a single list. Don’t include the same movie twice


def get_related_titles(lst_of_movies):
    first_lst = [extract_movie_titles(get_movies_from_tastedive(movie)) for movie in lst_of_movies]
    final_lst = []
    for lst in first_lst:
        for movie in lst:
            if movie not in final_lst:
                final_lst.append(movie)

    return final_lst

# Your next task will be to fetch data from OMDB. The documentation for the API is at https://www.omdbapi.com/
# Define a function called get_movie_data. It takes in one parameter which is a string that should represent the
# title of a movie you want to search. The function should return a dictionary with information about that movie.
# Again, use requests_with_caching.get(). For the queries on movies that are already in the cache, you won’t need
# an api key. You will need to provide the following keys: t and r. As with the TasteDive cache, be sure to only
# include those two parameters in order to extract existing data from the cache.


def get_movie_data(movie):
    par = {}
    par['t'] = movie
    par['r'] = 'json'
    url = 'http://www.omdbapi.com/'
    omdb_results = requests_with_caching.get(url, params = par)
    omdb_results_final = json.loads(omdb_results.text)
    return omdb_results_final

# Now write a function called get_movie_rating. It takes an OMDB dictionary result for one movie and
# extracts the Rotten Tomatoes rating as an integer. For example, if given the OMDB dictionary for
# “Black Panther”, it would return 97. If there is no Rotten Tomatoes rating, return 0.


def get_movie_rating(dic):
    omdb_dic = dic
    for dict in omdb_dic['Ratings']:
        if dict['Source'] == "Rotten Tomatoes":
            score = int(dict['Value'].strip('%'))
            return score
    return 0


# Define a function get_sorted_recommendations. It takes a list of movie titles as an input.
# It returns a sorted list of related movie titles as output, up to five related movies for each input movie title.
# The movies should be sorted in descending order by their Rotten Tomatoes rating, as returned by the get_movie_rating
# function. Break ties in reverse alphabetic order, so that ‘Yahşi Batı’ comes before ‘Eyyvah Eyvah’.

def get_sorted_recommendations(lst_of_movies):
    taste_lst = get_related_titles(lst_of_movies)
    sorted_lst = sorted(taste_lst, key=lambda movie: (get_movie_rating(get_movie_data(movie)), movie[-1]), reverse=True)
    return sorted_lst