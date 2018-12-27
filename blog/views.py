# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import auth
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
import json
from models import Blog, Comment, Tags, Saying
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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


@csrf_exempt
def index(request):
    resp = {'success': 0, 'error': '', 'data': [], 'tags': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        username = request.session.get('username', '')
        resp['success'] = 1
        resp['data'].append(username)
        all_blog = Blog.objects.order_by('-blog_time')[(page-1)*size:page*size]
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
        resp['total'] = Blog.objects.all().count()
        return HttpResponse(json.dumps(resp), content_type='application/json')
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


@csrf_exempt
def about(request):
    return render(request, 'about.html')


def get_com_dict(comment):
    comment_att = {}
    comment_att['father'] = comment.father_id
    comment_att['father_name'] = comment.father.comment_author.username if comment.father else ''
    comment_att['comment_id'] = comment.id
    comment_att['comment_content'] = comment.comment_content
    comment_att['comment_author'] = comment.comment_author.username
    comment_att['comment_time'] = str(comment.comment_time).split('+')[0]
    return comment_att


def get_comments(blog_name=''):
    result = []
    for comment in Comment.objects.filter(blog__blog_name=blog_name, father__isnull=True):
        father_dict = get_com_dict(comment)
        father_dict['children'] = []
        for child_com in Comment.objects.filter(ancestor=comment).order_by('comment_time'):
            father_dict['children'].append(get_com_dict(child_com))
        result.append(father_dict)
    return result


@csrf_exempt
def whole_passage(request):
    resp = {'success': 0, 'error': '', 'data': [], 'all_data': [], 'comments': []}
    blog_name = request.GET.get('blog_name')
    # comment_author = request.session['username']
    # blog_exist = get_object_or_404(Blog, pk=blog_name)
    if request.method == 'POST':
        resp['success'] = 1
        resp['comments'] = get_comments(blog_name)
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


@csrf_exempt
def all_article(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        all_blog = Blog.objects.all().order_by('-blog_time')[(page-1)*size:page*size]
        resp['success'] = 1
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
        resp['total'] = Blog.objects.all().count()
        request.session['data'] = resp['data']
        return HttpResponse(json.dumps(resp),content_type='application/json')
    else:
        return render(request, 'article.html')


@csrf_exempt
def comment(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        comment_content = request.POST.get('comment_content')
        comment_author = request.session.get('username', '')
        father_comment_id = request.POST.get('father_comment_id', '')
        if comment_author:
            username = User.objects.filter(username=comment_author).first()
            blog_name = request.POST.get('blog_name')
            blog = Blog.objects.filter(blog_name=blog_name).first()

            com = Comment(comment_author=username, comment_content=str(comment_content), blog=blog)
            if father_comment_id:# 回复评论
                father = Comment.objects.filter(id=father_comment_id).first()
                com.father = father
                com.ancestor = father.ancestor if father.ancestor else father
            com.save()
            resp['success'] = 1
        else:
            resp['error'] = '请先登录后再评论'
        return HttpResponse(json.dumps(resp))


@csrf_exempt
def saying(request):
    say_list = []
    all_saying = Saying.objects.all().order_by('-say_time')
    for saying in all_saying:
        say_dict = {}
        say_dict['say_context'] = saying.say_context
        say_dict['say_time'] = str(saying.say_time).split('+')[0]
        say_dict['image'] = saying.image
        say_list.append(say_dict)
    return render(request, 'moodList.html', {'all_saying': say_list})