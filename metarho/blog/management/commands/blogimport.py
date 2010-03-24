from django.core.management.base import BaseCommand

from metarho.blog.importer import WordPressExportParser

class Command(BaseCommand):


    def handle(self, *args, **options):
        for file in args:
            wp = WordPressExportParser(file)
            wp.parse()
        

    