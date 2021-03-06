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
    blog_time = models.DateTimeField(auto_now_add=True)
    blog_name = models.CharField(max_length=50)
    blog_context = models.TextField(max_length=5000)
    author = models.ForeignKey(User)
    comment_quantity = models.IntegerField(default=0)
    reading_quantity = models.IntegerField(default=0)
    image = models.ImageField(upload_to='blog_configure_image', blank=True)
    blog_label = models.ManyToManyField(Tags, blank=True)


    def __unicode__(self):
        return self.blog_name


class Comment(models.Model):
    father = models.ForeignKey('self', models.SET_NULL, verbose_name='父', null=True,related_name='father_comment')
    ancestor = models.ForeignKey('self', models.SET_NULL, verbose_name='祖宗', null=True,related_name='ancestor_comment')
    comment_author = models.ForeignKey(User)
    comment_content = models.TextField(max_length=200)
    comment_time = models.DateTimeField(auto_now_add=True)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return self.comment_content


class MesBoard(models.Model):
    father = models.ForeignKey('self', models.SET_NULL, verbose_name='父', null=True, related_name='father_msg')
    ancestor = models.ForeignKey('self', models.SET_NULL, verbose_name='祖宗', null=True, related_name='ancestor_msg')
    msg_author = models.ForeignKey(User)
    msg_content = models.TextField(max_length=200)
    msg_time = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.msg_content


class Saying(models.Model):
    say_context = models.TextField(max_length=5000)
    say_time = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='saying_configure_image', blank=True)


class Video(models.Model):
    video_path = models.FileField(upload_to="video")
    upload_user = models.ForeignKey(User)
    upload_time = models.DateTimeField(auto_now_add=True)
    video_title = models.CharField(max_length=50)
    video_size = models.IntegerField(default=0, editable=False, blank=True)


class Music(models.Model):
    music_path = models.FileField(upload_to="music")
    upload_user = models.ForeignKey(User)
    upload_time = models.DateTimeField(auto_now_add=True)
    music_title = models.CharField(max_length=50)
    singer = models.CharField(max_length=50)
    lyric_path = models.FileField(upload_to="music")

    def __unicode__(self):
        return self.music_title


class CommentVideo(models.Model):
    father = models.ForeignKey('self', models.SET_NULL, verbose_name='父', null=True, related_name='father_comment')
    ancestor = models.ForeignKey('self', models.SET_NULL, verbose_name='祖宗', null=True, related_name='ancestor_comment')
    comment_author = models.ForeignKey(User)
    comment_content = models.TextField(max_length=200)
    comment_time = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey(Video)

    def __unicode__(self):
        return self.comment_content