# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from blog import models
from django.contrib import admin

admin.site.register(models.Tags)
admin.site.site_header = '李东韩博客后台管理系统'
admin.site.site_title = '李东韩博客后台管理系统'


@admin.register(models.Comment)
class BlogAdmin(admin.ModelAdmin):
    # listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
    list_display = ('comment_content', 'comment_author', 'father', 'ancestor', 'comment_time', 'blog')

    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 50

    # ordering设置默认排序字段，负号表示降序排序
    ordering = ('-comment_time',)

    # list_editable 设置默认可编辑字段
    # list_editable = ['reading_quantity']

    # fk_fields 设置显示外键字段
    fk_fields = ('blog')
    list_filter = ('comment_author', 'father', 'ancestor', 'comment_time', 'blog')  # 过滤器
    search_fields = ('comment_content',)  # 搜索字段

@admin.register(models.Saying)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id', 'say_context', 'say_time')
    list_per_page = 50
    ordering = ('-say_time',)
    list_editable = ['say_context']
    # fk_fields = ('author')
    list_filter = ('say_time',)  # 过滤器
    search_fields = ('say_context',)  # 搜索字段


@admin.register(models.Blog)
class BlogAdmin(admin.ModelAdmin):
    # listdisplay设置要显示在列表中的字段（id字段是Django模型的默认主键）
    list_display = ('blog_name', 'author', 'blog_time', 'reading_quantity')
    # list_per_page设置每页显示多少条记录，默认是100条
    list_per_page = 50
    # ordering设置默认排序字段，负号表示降序排序
    ordering = ('-blog_time',)
    # list_editable 设置默认可编辑字段
    list_editable = ['reading_quantity']
    # fk_fields 设置显示外键字段
    fk_fields = ('author')
    list_filter = ('blog_name', 'author', 'blog_time', 'blog_label')  # 过滤器
    search_fields = ('blog_name',)  # 搜索字段
    # date_hierarchy = 'blog_time'


@admin.register(models.MesBoard)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('msg_content', 'father', 'ancestor', 'msg_author', 'msg_time')
    list_per_page = 50
    ordering = ('-msg_time',)
    list_filter = ('father', 'ancestor', 'msg_author', 'msg_time')  # 过滤器
    search_fields = ('msg_content',)  # 搜索字段


@admin.register(models.Video)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('video_title', 'upload_user', 'upload_time')
    list_per_page = 50
    ordering = ('-upload_time',)
    list_filter = ('upload_user', 'upload_time')  # 过滤器
    search_fields = ('video_title',)  # 搜索字段


@admin.register(models.Music)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('music_title', 'singer', 'upload_user', 'upload_time')
    list_per_page = 50
    ordering = ('-upload_time',)
    list_filter = ('upload_user', 'upload_time', 'singer')  # 过滤器
    search_fields = ('music_title', 'singer')  # 搜索字段