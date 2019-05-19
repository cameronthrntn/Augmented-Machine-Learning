import pandas as pd 
import numpy as np 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from ast import literal_eval
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

df1=pd.read_csv('recommendation/tmdb-5000-movie-dataset/tmdb_5000_credits.csv')
df2=pd.read_csv('recommendation/tmdb-5000-movie-dataset/tmdb_5000_movies.csv')

df1.columns = ['id','tittle','cast','crew']
df2= df2.merge(df1,on='id')

C= df2['vote_average'].mean()
m= df2['vote_count'].quantile(0.9)

tfidf = TfidfVectorizer(stop_words='english') 
df2['overview'] = df2['overview'].fillna('')
tfidf_matrix = tfidf.fit_transform(df2['overview']) 
cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix) 
indices = pd.Series(df2.index, index=df2['title']).drop_duplicates() 

def get_recommendations(title, cosine_sim, indices):
    idx = indices[title]   
    sim_scores = list(enumerate(cosine_sim[idx]))   
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)   
    sim_scores = sim_scores[1:11]   
    movie_indices = [i[0] for i in sim_scores]   
    return df2['title'].iloc[movie_indices]  

features = ['cast', 'crew', 'keywords', 'genres', 'production_companies']
for feature in features:
    df2[feature] = df2[feature].apply(literal_eval)
    
def get_director(x):
    for i in x:
        if i['job'] == 'Director':
            return str(i['name'])
    return " "

def get_companies(x):    
    return [i['name'] for i in x]

def get_list(x):  
    if isinstance(x, list):
        names = [i['name'] for i in x]
        if len(names) > 3:
            names = names[:3]
        return names
    return []  

df2['director'] = df2['crew'].apply(get_director)   

features = ['cast', 'keywords', 'genres']
for feature in features:
    df2[feature] = df2[feature].apply(get_list)
    
    

def clean_data(x): 
    if isinstance(x, list):
        return [str.lower(i.replace(" ", "")) for i in x]
    else:
        if isinstance(x, str):  
            return str.lower(x.replace(" ", ""))
        else:
            return ''
        
features = ['cast', 'keywords', 'director', 'genres'] 

for feature in features:
    df2[feature] = df2[feature].apply(clean_data)
    
def create_general_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['cast']) + ' ' + x['director'] + ' ' + ' '.join(x['genres'])

def create_director_soup(x):
    val = ' '
    for i in x['keywords']:
        val += ' ' + x['director']
    return ' '.join(x['keywords']) + val

def create_plot_soup(x):
    return ' '.join(x['keywords']) + ' ' + x['overview']

def create_genre_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['genres'])

def create_company_soup(x):
    return ' '.join(x['keywords']) + ' ' + ' '.join(x['company_list'])

def return_recommendation(movie, choice):
    switchDict = {"general": create_general_soup, "director": create_director_soup, "plot": create_plot_soup, 
              "genre": create_genre_soup, "company": create_company_soup}
    df2['director'] = df2['crew'].apply(get_director).tolist()
    df2['company_list'] = df2['production_companies'].apply(get_companies).tolist()
    df2['soup'] = df2.apply(switchDict.get(choice, "invalid choice"), axis=1)
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df2['soup'])
    cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
    indices = pd.Series(df2.index, index=df2['title'])
    recommendationlist = (get_recommendations(movie, cosine_sim2, indices))
    rec_indices = recommendationlist.index.values.tolist()
    recObj = []
    rectitles = []
    recoverviews = []
    genres = []
    directors = []
    companies = []
    for i in rec_indices:
        recObj.append(df2.loc[(df2.index.values == i)])
    for entry in recObj:
        rectitles.append(entry.iloc[0]['original_title'])
        recoverviews.append(entry.iloc[0]['overview'])
        genres.append(entry.iloc[0]['genres'])
        directors.append(get_director(entry.iloc[0]['crew']))
        companies.append(get_companies(entry.iloc[0]['production_companies']))
    return_list = []
    for x in range(10):
        return_list.append({"title":rectitles[x], "overview":recoverviews[x], "genres":genres[x], "director":directors[x], "companies":companies[x]})
    return return_list

def return_general(movie):
    df2['director'] = df2['crew'].apply(get_director).tolist()
    df2['company_list'] = df2['production_companies'].apply(get_companies).tolist()
    df2['soup'] = df2.apply(create_general_soup, axis=1)
    count = CountVectorizer(stop_words='english')
    count_matrix = count.fit_transform(df2['soup'])
    cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
    indices = pd.Series(df2.index, index=df2['title'])
    recommendationlist = (get_recommendations(movie, cosine_sim2, indices))
    rec_indices = recommendationlist.index.values.tolist()
    recObj = []
    rectitles = []
    recoverviews = []
    genres = []
    directors = []
    companies = []
    for i in rec_indices:
        recObj.append(df2.loc[(df2.index.values == i)])
    for entry in recObj:
        rectitles.append(entry.iloc[0]['original_title'])
        recoverviews.append(entry.iloc[0]['overview'])
        genres.append(entry.iloc[0]['genres'])
        directors.append(get_director(entry.iloc[0]['crew']))
        companies.append(get_companies(entry.iloc[0]['production_companies']))
    return_list = []
    for x in range(10):
        return_list.append({"title":rectitles[x], "overview":recoverviews[x], "genres":genres[x], "director":directors[x], "companies":companies[x]})
    return return_list

#recommendation_info = return_general("The Dark Knight Rises")

movielist = df2['original_title'].tolist()
infolist = df2['overview'].tolist()
directors = df2['crew'].apply(get_director).tolist()
genre = df2['genres'].tolist()
companieslist = df2['production_companies'].apply(get_companies).tolist()
runtimelist = df2['runtime'].tolist()