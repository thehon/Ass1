# Generated by Django 3.0.2 on 2020-03-27 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ed', '0011_auto_20200327_0716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(through='ed.ChatMembership', to='ed.Profile'),
        ),
    ]
