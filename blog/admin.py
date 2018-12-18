# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from blog import models
from django.contrib import admin

admin.site.register(models.Blog)
admin.site.register(models.Tags)
admin.site.register(models.Comment)

# Register your models here.
