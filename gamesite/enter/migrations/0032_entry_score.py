# Generated by Django 3.1.3 on 2021-01-08 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('enter', '0031_auto_20210107_1942'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]