# Generated by Django 2.1.7 on 2019-03-23 01:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('test05_fk_in', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='a',
            options={'base_manager_name': 'objects'},
        ),
    ]
