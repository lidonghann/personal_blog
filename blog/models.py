# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Tags(models.Model):
    tag = models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.tag


class Blog(models.Model):
    top = models.IntegerField(default=0)
    blog_time = models.DateTimeField(auto_now=True)
    blog_name = models.CharField(max_length=50)
    blog_context = models.TextField(max_length=1000)
    author = models.ForeignKey(User)
    comment_quantity = models.IntegerField(default=0)
    reading_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='blog_configure_image', blank=True)
    blog_label = models.ManyToManyField(Tags, blank=True)

    def __unicode__(self):
        return self.blog_name


class Comment(models.Model):
    comment_author = models.ForeignKey(User)
    comment_content = models.CharField(max_length=200)
    comment_time = models.DateTimeField(auto_now=True)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return self.comment_author