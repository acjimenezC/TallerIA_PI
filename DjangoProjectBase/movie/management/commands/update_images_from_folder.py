import os
import re
from unidecode import unidecode
from django.core.management.base import BaseCommand
from movie.models import Movie

class Command(BaseCommand):
    help = (
        "Asigna imágenes a películas desde media/movie/images/ "
        "coincidiendo aunque el título tenga o no caracteres especiales."
    )

    def handle(self, *args, **options):
        images_dir = os.path.join("media", "movie", "images")
        if not os.path.isdir(images_dir):
            self.stderr.write(f"No existe la carpeta: {images_dir}")
            return

        def normalize(txt):
            txt = unidecode(txt)
            txt = txt.lower()
            txt = re.sub(r"[^0-9a-z ]+", "", txt)
            txt = re.sub(r"\s+", " ", txt).strip()
            return txt

        # Índice de archivos existentes
        file_map = {}
        for fname in os.listdir(images_dir):
            path = os.path.join(images_dir, fname)
            if not os.path.isfile(path):
                continue
            name, ext = os.path.splitext(fname)
            if ext.lower() not in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
                continue
            key = normalize(name[2:] if name.startswith("m_") else name)
            file_map[key] = fname

        updated = 0
        default_image = "movie/images/default.png"

        for movie in Movie.objects.all():
            norm_title = normalize(movie.title)
            chosen = file_map.get(norm_title)

            if not chosen:
                for key, fname in file_map.items():
                    if key and (key in norm_title or norm_title in key):
                        chosen = fname
                        break

            if chosen:
                movie.image = f"movie/images/{chosen}"
                movie.save()
                updated += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Imagen asignada: {movie.title} → {chosen}")
                )
            else:
                movie.image = default_image
                movie.save()
                self.stderr.write(
                    f"No se encontró imagen para: {movie.title}. Se usó la imagen por defecto."
                )

        self.stdout.write(self.style.SUCCESS(
            f"Total películas actualizadas: {updated}"
        ))
