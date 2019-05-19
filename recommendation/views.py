from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.http import Http404
from django.views.decorators.csrf import csrf_exempt
import engine as eng
import urllib.request
import urllib.parse
import re
import json

def index(request):
    lom = eng.movielist
    return render(request, 'recommendation/index.html', {'lom':lom})
    
@csrf_exempt
def movie(request):
    if request.method == 'GET':
        movie_title = request.GET.get('movieChoice', False)
        lom = eng.movielist
        if movie_title in lom:
            index = eng.movielist.index(movie_title)
            overview = eng.infolist[index]
            director = eng.directors[index]
            genres = str(eng.genre[index]).replace("'","")[1:-1]
            companies = str(eng.companieslist[index]).replace("'","")[1:-1]
            runtime = str(int(eng.runtimelist[index]) // 60) + "h" + str(int(eng.runtimelist[index]) % 60) + "m"
            query_string = urllib.parse.urlencode({"search_query" : movie_title + "trailer"})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            video = "http://www.youtube.com/embed/" + search_results[0] + "?autoplay=1"
        else:
            raise Http404("No data found for movie, please try something else.")
        return render(request, 'recommendation/movie.html', {'movie_title': movie_title, 'overview':overview, 'lom':lom, 'video':video, 'director':director, 'genres':genres, 'companies':companies, 'runtime':runtime})
    if request.method == 'POST':
        recommendation_choice = request.POST.get('recommendationChoice', False)
        movie_title = request.POST.get('movieChoice', False)
        
        recommendation_info = eng.return_recommendation(movie_title, recommendation_choice)
        recommendation_general_info = eng.return_general(movie_title)
        
        rec_titles = []
        rec_overviews = []
        genres = []
        directors = []
        companies = []
        videos = []
        for i in recommendation_info:
            query_string = urllib.parse.urlencode({"search_query" : i.get("title", "invalid choice") + "trailer"})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            video = "http://www.youtube.com/embed/" + search_results[0]
            videos.append(video)
            rec_titles.append(i.get("title", "invalid choice"))
            rec_overviews.append(i.get("overview", "invalid choice"))
            genres.append(i.get("genres", "invalid choice"))
            directors.append(i.get("director", "invalid choice"))
            companies.append(i.get("companies", "invalid choice"))
            
        for i in recommendation_general_info:
            query_string = urllib.parse.urlencode({"search_query" : i.get("title", "invalid choice") + "trailer"})
            html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
            search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
            video = "http://www.youtube.com/embed/" + search_results[0]
            videos.append(video)
            rec_titles.append(i.get("title", "invalid choice"))
            rec_overviews.append(i.get("overview", "invalid choice"))
            genres.append(i.get("genres", "invalid choice"))
            directors.append(i.get("director", "invalid choice"))
            companies.append(i.get("companies", "invalid choice"))
        
        response_data = {}

        response_data['choice'] = recommendation_choice
        response_data['titles'] = rec_titles
        response_data['overviews'] = rec_overviews
        response_data['genres'] = genres
        response_data['directors'] = directors
        response_data['companies'] = companies
        response_data['vid_links'] = videos
        
        return HttpResponse(json.dumps(response_data), content_type='application/json')
