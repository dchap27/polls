# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-02 23:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0020_question_eligibility'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='eligible_gender',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
