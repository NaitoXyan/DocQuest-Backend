# Generated by Django 5.0.7 on 2024-08-31 13:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('docquestapp', '0005_alter_project_moaid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='goalsandobjectives',
            old_name='GOAID',
            new_name='GAOID',
        ),
    ]