# Generated by Django 3.2.16 on 2023-01-12 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_recipe_tags'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='recipe',
            name='tags',
        ),
    ]
