# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-23 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_remove_choice_sex'),
    ]

    operations = [
        migrations.AddField(
            model_name='choice',
            name='f_sex',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='choice',
            name='m_sex',
            field=models.IntegerField(default=0),
        ),
    ]
