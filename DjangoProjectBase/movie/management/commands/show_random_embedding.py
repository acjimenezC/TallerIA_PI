import numpy as np
import random
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = "Muestra de forma formateada los embeddings de una película al azar."

    def handle(self, *args, **options):
        movies = list(Movie.objects.all())
        if not movies:
            self.stderr.write("⚠️  No hay películas en la base de datos.")
            return

        movie = random.choice(movies)
        embedding_vector = np.frombuffer(movie.emb, dtype=np.float32)

        # Cabecera con color
        self.stdout.write(self.style.SUCCESS("\n🎬  EMBEDDING DE PELÍCULA AL AZAR 🎬"))
        self.stdout.write(self.style.SUCCESS("─" * 60))

        # Información principal
        self.stdout.write(f"📽️  Título        : {movie.title}")
        self.stdout.write(f"🔢  Dimensión     : {embedding_vector.shape[0]}")
        self.stdout.write("📊  Primeros 10 valores del embedding:")

        # Imprime 10 valores en columnas alineadas
        pretty_vals = " | ".join(f"{v: .4f}" for v in embedding_vector[:10])
        self.stdout.write(f"     {pretty_vals}")

        self.stdout.write(self.style.SUCCESS("─" * 60))
        self.stdout.write("")  # línea en blanco final
