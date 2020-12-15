import sys
from os import chdir, getcwd
from http.server import HTTPServer, SimpleHTTPRequestHandler

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Starts frontend server"

    def handle(self, *args, **kwargs):
        chdir(settings.BASE_DIR / "frontend-compiled")
        try:
            print("Frontend Server running on http://localhost:3000")
            print("> Press Ctrl-C to exit")
            httpd = HTTPServer(("", 3000), SimpleHTTPRequestHandler)
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Stopping frontend server...")
        finally:
            httpd.server_close()
