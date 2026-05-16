from django.apps import AppConfig
from django.db import connection


class VisualizerConfig(AppConfig):
    name = 'visualizer'

    def ready(self):
        """Perform system-wide optimizations on startup."""
        # Enable WAL mode for SQLite
        try:
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
