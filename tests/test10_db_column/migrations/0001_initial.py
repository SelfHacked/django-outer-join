# Generated by Django 2.1.8 on 2019-05-28 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='A',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.IntegerField(unique=True)),
                ('field1', models.IntegerField(null=True)),
                ('field2', models.IntegerField(null=True)),
                ('field3', models.IntegerField(null=True)),
                ('is_deleted', models.BooleanField(null=True)),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='A0',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.IntegerField(db_column='xxx', unique=True)),
                ('field1', models.IntegerField(db_column='yyy')),
                ('field2', models.IntegerField(db_column='zzz')),
            ],
        ),
        migrations.CreateModel(
            name='A1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('key', models.IntegerField(db_column='aaa', unique=True)),
                ('field1', models.IntegerField(db_column='bbb', null=True)),
                ('field3', models.IntegerField(db_column='ccc', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]