# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import auth
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
import json
from models import Blog,Comment,Tags
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@csrf_exempt
def login(request):
    resp = {'success': 0, 'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        result = auth.authenticate(username=username, password=password)
        request.session['username'] = str(result)
        if result is not None:
            auth.login(request, result)
            resp['success'] = 1
        else:
            resp['error'] = '用户名或密码错误'
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'login.html')


def logout(request):
    del request.session['username']
    auth.logout(request)
    return render(request, 'login.html')


@login_required
@csrf_exempt
def index(request):
    resp = {'success': 0, 'error': '', 'data': [], 'tags': []}
    if request.method == 'POST':
        username = request.session['username']
        resp['success'] = 1
        resp['data'].append(username)
        all_blog = Blog.objects.order_by('-blog_time')
        for blog in all_blog:
            blog_att = {}
            blog_att['top'] = blog.top
            blog_att['blog_name'] = blog.blog_name
            blog_att['blog_context'] = blog.blog_context
            blog_att['blog_time'] = str(blog.blog_time).split('+')[0]
            blog_att['author'] = blog.author.username
            blog_att['comment_quantity'] = blog.comment_quantity
            blog_att['reading_quantity'] = blog.reading_quantity
            blog_att['image'] = str(blog.image)
            blog_att['blog_label'] = [label.tag for label in blog.blog_label.all()]
            resp['data'].append(blog_att)
        tags = Tags.objects.all()
        tags_set = set([tag for tag in tags])
        [resp['tags'].append(tag.tag) for tag in tags_set]
        # print resp['tags']
        # all_blog[0].reading_quantity += 1
        # print all_blog[0].blog_name
        # Blog.objects.filter(blog_name=all_blog[0].blog_name).update(reading_quantity=all_blog[0].reading_quantity)
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'index.html')


@csrf_exempt
def register(request):
    resp = {'success': 0, 'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')
        email = request.POST.get('email', '')
        if username and password and password2:
            if password2 == password:
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()
                request.session['username'] = username
                resp['success'] = 1
            else:
                resp['error'] = '两次密码不一样'
        else:
            resp['error'] = '请填写完整'
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'login.html')


@csrf_exempt
def check_user_is_exist(request):
    resp = {'success': 0, 'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        if User.objects.filter(username=username).exists():
            resp['error'] = '账号已存在'
        else:
            resp['success'] = 1
        return HttpResponse(json.dumps(resp))


@login_required
@csrf_exempt
def about(request):
    return render(request, 'about.html')


@login_required
@csrf_exempt
def whole_passage(request):
    resp = {'success': 0, 'error': '', 'data': [], 'all_data':[]}
    blog_name = request.GET.get('blog_name')
    if request.method == 'POST':
        resp['success'] = 1
        blog = Blog.objects.filter(blog_name=blog_name).first()
        blog_att = {}
        blog_att['top'] = blog.top
        blog_att['blog_name'] = blog.blog_name
        blog_att['blog_context'] = blog.blog_context
        blog_att['blog_time'] = str(blog.blog_time).split('+')[0]
        blog_att['author'] = blog.author.username
        blog_att['comment_quantity'] = blog.comment_quantity
        blog_att['reading_quantity'] = blog.reading_quantity
        blog_att['image'] = str(blog.image)
        blog_att['blog_label'] = [label.tag for label in blog.blog_label.all()]
        resp['data'].append(blog_att)
        resp['all_data'] = request.session['data']
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'article_detail.html', {'blog_name': blog_name})


@login_required
@csrf_exempt
def all_article(request):
    resp = {'success': 0, 'error': '', 'data': [], 'page_need': {}}
    if request.method == 'POST':
        all_blog = Blog.objects.order_by('-blog_time')
        resp['success'] = 1
        resp['page_need']['pageCount'] = len(all_blog)/2
        resp['page_need']['totalData'] = len(all_blog)
        resp['page_need']['showData'] = 2
        for blog in all_blog:
            blog_att = {}
            blog_att['top'] = blog.top
            blog_att['blog_name'] = blog.blog_name
            blog_att['blog_context'] = blog.blog_context
            blog_att['blog_time'] = str(blog.blog_time).split('+')[0]
            blog_att['author'] = blog.author.username
            blog_att['comment_quantity'] = blog.comment_quantity
            blog_att['reading_quantity'] = blog.reading_quantity
            blog_att['image'] = str(blog.image)
            blog_att['blog_label'] = [label.tag for label in blog.blog_label.all()]
            resp['data'].append(blog_att)
        request.session['data'] = resp['data']
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'article.html')

