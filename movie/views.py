from django.shortcuts import render
from django.http import HttpResponse

from .models import Movie
import matplotlib.pyplot as plt
import matplotlib
import io
import urllib, base64

# Create your views here.

def home (request):
    #return HttpResponse('<h1>Welcome to Home Page</h1>')
    #return render(request, 'home.html')
    #return render(request, 'home.html', {'name':'Alexandra Hurtado'})
    searchTerm = request.GET.get('searchMovie')
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, 'home.html',{'searchTerm':searchTerm, 'movies':movies})

def about (request):
    return render(request, 'about.html')

def signup (request):
    email = request.GET.get('email')
    return render(request, 'signup.html', {'email':email})

def statistics_view(request):
    matplotlib.use('Agg')  # Para que no se muestre la gráfica en ventana emergente

    # Gráfico de cantidad de películas por año
    years = Movie.objects.values_list('year', flat=True).distinct().order_by('year')
    movie_counts_by_year = {year: Movie.objects.filter(year=year).count() for year in years if year}
    
    bar_width = 0.5  # Ancho de las barras
    bar_positions = range(len(movie_counts_by_year))

    plt.figure(figsize=(10, 5))
    plt.bar(bar_positions, movie_counts_by_year.values(), width=bar_width, align='center', color='skyblue')
    plt.title('Movies per Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Movies')
    plt.xticks(bar_positions, movie_counts_by_year.keys(), rotation=90)
    plt.subplots_adjust(bottom=0.3)

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_years = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Gráfico de cantidad de películas por género (primer género de cada película)
    movies = Movie.objects.exclude(genre__isnull=True).exclude(genre='').values_list('genre', flat=True)
    genre_counts = {}
    for movie_genres in movies:
        first_genre = movie_genres.split(',')[0].strip()  # Tomar solo el primer género
        genre_counts[first_genre] = genre_counts.get(first_genre, 0) + 1

    plt.figure(figsize=(10, 5))
    plt.bar(genre_counts.keys(), genre_counts.values(), color='coral')
    plt.xlabel('Genre')
    plt.ylabel('Number of Movies')
    plt.title('Movies per Genre')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    plt.close()
    graphic_genres = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Renderizar la plantilla con ambas gráficas
    return render(request, 'statistics.html', {'graphic_years': graphic_years, 'graphic_genres': graphic_genres})
