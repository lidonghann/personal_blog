# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-12-11 09:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0005_auto_20181211_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blog',
            name='image',
            field=models.ImageField(blank=True, upload_to='blog_configure_image'),
        ),
    ]
