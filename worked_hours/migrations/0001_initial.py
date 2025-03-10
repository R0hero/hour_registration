# Generated by Django 5.0.6 on 2024-07-08 19:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project_name', models.CharField(max_length=128, verbose_name='Project name')),
                ('project_number', models.IntegerField(verbose_name='Project number')),
                ('description', models.TextField(blank=True, verbose_name='Description of project')),
                ('date', models.DateTimeField(verbose_name='Event date')),
                ('hours', models.FloatField(verbose_name='Hours spent per date')),
            ],
        ),
    ]
