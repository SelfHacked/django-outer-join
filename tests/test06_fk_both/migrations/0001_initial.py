# Generated by Django 2.1.7 on 2019-03-22 18:28

import django.db.models.manager
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='A',
            fields=[
            ],
            options={
                'managed': False,
                'base_manager_name': 'base_objects',
            },
        ),
        migrations.CreateModel(
            name='B',
            fields=[
            ],
            options={
                'managed': False,
                'base_manager_name': 'base_objects',
            },
        ),
        migrations.CreateModel(
            name='A0',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.IntegerField(unique=True)),
                ('val', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='A1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('key', models.IntegerField(unique=True)),
                ('val', models.IntegerField(null=True)),
                ('b', models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.CASCADE,
                                        related_name='+', to='test06_fk_both.B')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='B0',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.IntegerField(unique=True)),
                ('val', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='B1',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_deleted', models.BooleanField(default=False)),
                ('key', models.IntegerField(unique=True)),
                ('val', models.IntegerField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='a0',
            name='b',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+',
                                    to='test06_fk_both.B0'),
        ),
    ]
