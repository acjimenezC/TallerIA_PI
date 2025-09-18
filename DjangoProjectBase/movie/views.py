from django.shortcuts import render
from django.http import HttpResponse
import os
import io
import base64
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from openai import OpenAI
from .models import Movie

# ==================== CONFIGURACIÓN OPENAI ====================
load_dotenv("keys.env")
client = OpenAI(api_key=os.environ.get("openai_apikey"))


# ==================== VISTAS PRINCIPALES ====================

def home(request):
    """Página principal con búsqueda de películas por título."""
    searchTerm = request.GET.get("searchMovie")
    if searchTerm:
        movies = Movie.objects.filter(title__icontains=searchTerm)
    else:
        movies = Movie.objects.all()
    return render(request, "home.html", {"searchTerm": searchTerm, "movies": movies})


def about(request):
    """Página de información del sitio."""
    return render(request, "about.html")


def signup(request):
    """Página de registro simple."""
    email = request.GET.get("email")
    return render(request, "signup.html", {"email": email})


# ==================== ESTADÍSTICAS ====================

def statistics_view(request):
    """
    Muestra dos gráficas:
      1. Películas por año.
      2. Películas por género (primer género listado).
    """
    matplotlib.use("Agg")  # backend para generar imágenes sin ventana
    all_movies = Movie.objects.all()

    # --- Películas por año ---
    movie_counts_by_year = {}
    for movie in all_movies:
        year = movie.year if movie.year else "None"
        movie_counts_by_year[year] = movie_counts_by_year.get(year, 0) + 1

    year_graphic = generate_bar_chart(
        movie_counts_by_year,
        xlabel="Año",
        ylabel="Número de películas",
        title="Películas por Año",
    )

    # --- Películas por género ---
    movie_counts_by_genre = {}
    for movie in all_movies:
        genre = movie.genre.split(",")[0].strip() if movie.genre else "None"
        movie_counts_by_genre[genre] = movie_counts_by_genre.get(genre, 0) + 1

    genre_graphic = generate_bar_chart(
        movie_counts_by_genre,
        xlabel="Género",
        ylabel="Número de películas",
        title="Películas por Género",
    )

    return render(
        request,
        "statistics.html",
        {"year_graphic": year_graphic, "genre_graphic": genre_graphic},
    )


def generate_bar_chart(data, xlabel, ylabel, title="Distribución de Películas"):
    """Genera una gráfica de barras en base64 para embeber en HTML."""
    keys = [str(key) for key in data.keys()]
    plt.figure(figsize=(8, 4))
    plt.bar(keys, data.values())
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=90)
    plt.tight_layout()

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plt.close()

    graphic = base64.b64encode(buffer.getvalue()).decode("utf-8")
    buffer.close()
    return graphic


# ==================== SISTEMA DE RECOMENDACIÓN ====================

def cosine_similarity(a, b):
    """Calcula la similitud de coseno entre dos vectores."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def recommend_movie(request):
    """
    Página para recomendar una película basada en un prompt del usuario.
    Genera embedding con OpenAI y compara con cada película en la BD.
    """
    recommendation = None
    similarity_score = None

    if request.method == "POST":
        prompt = request.POST.get("prompt", "").strip()
        if prompt:
            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small"
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

            best_movie = None
            max_sim = -1
            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                sim = cosine_similarity(prompt_emb, movie_emb)
                if sim > max_sim:
                    max_sim = sim
                    best_movie = movie

            recommendation = best_movie
            similarity_score = f"{max_sim:.4f}"

    # 🔑 Importante: la plantilla está en templates/recommend.html
    return render(
        request,
        "recommend.html",
        {"recommendation": recommendation, "similarity": similarity_score},
    )
