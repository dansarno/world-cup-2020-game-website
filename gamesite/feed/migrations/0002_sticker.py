# Generated by Django 3.1.3 on 2021-02-06 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feed', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Sticker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('sticker_picture', models.ImageField(upload_to='sticker_pics')),
            ],
        ),
    ]