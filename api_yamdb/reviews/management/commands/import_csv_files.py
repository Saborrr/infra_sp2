import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from reviews import models
from users.models import User

root = Path(__file__).parent.parent.parent.parent
static_data_dir = Path(root, 'static', 'data')

FILE_LIST = {
    Path(static_data_dir, 'category.csv'): models.Category,
    Path(static_data_dir, 'genre.csv'): models.Genre,
    Path(static_data_dir, 'titles.csv'): models.Title,
    Path(static_data_dir, 'genre_title.csv'): models.GenreTitle,
    Path(static_data_dir, 'users.csv'): User,
    Path(static_data_dir, 'review.csv'): models.Review,
    Path(static_data_dir, 'comments.csv'): models.Comment,
}


class Command(BaseCommand):
    help = 'Импорт данных из csv файлов'

    def handle(self, *args, **options):
        for file_name, model in FILE_LIST.items():
            with open(file_name, 'r', newline='', encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile, quotechar='"')
                is_first_line = True
                lines = list()
                for row in reader:
                    if is_first_line:
                        head = row
                        is_first_line = False
                    else:
                        line = dict(zip(head, row))
                        lines.append(line)
                creted_num = self.CreateNewObject(model, lines)
                print(f'Created {creted_num} record, object {model}')

    def CreateNewObject(self, model, lines):
        created = 0
        for line in lines:
            print(line)
            model.objects.get_or_create(**line)
            created = created + 1
        return created
