# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-20 19:49
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0016_auto_20160420_2048'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountsettings',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
