import csv

from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Import ingredients from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the CSV file with ingredients'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        
        if Ingredient.objects.exists():
            self.stdout.write('Ingredients already exist in the database')
            return

        try:
            ingredients_to_create = []
            with open(file_path, encoding='utf-8') as file:
                reader = csv.reader(file)
                for row in reader:
                    name, measurement_unit = row
                    ingredients_to_create.append(
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=measurement_unit.strip()
                        )
                    )
            
            Ingredient.objects.bulk_create(
                ingredients_to_create,
                batch_size=100
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Ingredients successfully imported from {file_path}'
                )
            )
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR(f'File not found: {file_path}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error importing ingredients: {e}')
            ) 