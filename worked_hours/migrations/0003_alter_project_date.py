# Generated by Django 5.0.6 on 2024-07-08 20:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('worked_hours', '0002_alter_project_date_alter_project_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='date',
            field=models.DateField(verbose_name='Project date'),
        ),
    ]
