# Generated by Django 3.1.3 on 2020-12-29 00:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('enter', '0018_auto_20201229_0030'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='enter.group'),
        ),
    ]
