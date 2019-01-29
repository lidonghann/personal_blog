# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import auth
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.http import HttpResponse
import json
from models import Blog, Comment, Tags, Saying, MesBoard, Video, Music, CommentVideo
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import sys
import re
import requests
from bs4 import BeautifulSoup
from django.db.models import Q
from dwebsocket.decorators import accept_websocket
import time
from util import RedisConnect, VideoFileCheck
import urllib
import os

reload(sys)
sys.setdefaultencoding('utf-8')
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}

@csrf_exempt
def login(request):
    resp = {'success': 0, 'error': ''}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        result = auth.authenticate(username=username, password=password)
        if result is not None:
            auth.login(request, result)
            request.session['username'] = str(result)
            resp['success'] = 1
        else:
            resp['error'] = '用户名或密码错误'
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'login.html')


def logout(request):
    del request.session['username']
    auth.logout(request)
    return redirect('/login/')


@csrf_exempt
def index(request):
    resp = {'success': 0, 'error': '', 'username': 0, 'data': [], 'tags': []}
    if request.method == 'POST':
        username = request.session.get('username', '')
        if username:
            resp['username'] = 1
        resp['success'] = 1
        resp['data'].append(username)
        all_blog = Blog.objects.order_by('-blog_time')[0:10]
        for blog in all_blog:
            resp['data'].append(get_blog(blog))
        tags = Tags.objects.all()
        tags_set = set([tag for tag in tags])
        [resp['tags'].append(tag.tag) for tag in tags_set]
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


def get_comments(blog_name='', page=1, size=5):
    result = []
    for comment in Comment.objects.filter(blog__blog_name=blog_name, father__isnull=True)[
                   (page - 1) * size:page * size]:
        father_dict = get_com_dict(comment)
        father_dict['children'] = []
        for child_com in Comment.objects.filter(ancestor=comment).order_by('comment_time'):
            father_dict['children'].append(get_com_dict(child_com))
        result.append(father_dict)
    total = Comment.objects.filter(blog__blog_name=blog_name, father__isnull=True).count()
    return result, total


@csrf_exempt
def whole_passage(request):
    resp = {'success': 0, 'error': '', 'data': [], 'all_data': [], 'comments': []}
    blog_name = request.GET.get('blog_name')
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        resp['success'] = 1
        resp['comments'], total = get_comments(blog_name, page, size)
        blog = Blog.objects.filter(blog_name=blog_name).first()
        resp['data'].append(get_blog(blog))
        blog.reading_quantity += 1
        blog.save()
        all_blog = Blog.objects.all().order_by('-blog_time')
        for blog in all_blog:
            resp['all_data'].append(get_blog(blog))
        resp['total'] = total
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'article_detail.html', {'blog_name': blog_name})


def get_blog(blog):
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
    return blog_att


@csrf_exempt
def all_article(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        all_blog = Blog.objects.all().order_by('-blog_time')[(page - 1) * size:page * size]
        resp['success'] = 1
        for blog in all_blog:
            resp['data'].append(get_blog(blog))
        resp['total'] = Blog.objects.all().count()
        # request.session['data'] = resp['data']
        return HttpResponse(json.dumps(resp), content_type='application/json')
    else:
        return render(request, 'article.html')


@csrf_exempt
def search_blog(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        search_blog = request.POST.get('search_blog', '')
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        all_blog = Blog.objects.filter(Q(blog_name__icontains=search_blog) | Q(blog_context__icontains=search_blog) | Q(
            blog_label__tag__icontains=search_blog)).order_by('-blog_time')[(page - 1) * size:page * size]
        resp['success'] = 1
        for blog in all_blog:
            resp['data'].append(get_blog(blog))
        resp['total'] = Blog.objects.filter(
            Q(blog_name__icontains=search_blog) | Q(blog_context__icontains=search_blog)).count()
        # request.session['data'] = resp['data']
        return HttpResponse(json.dumps(resp), content_type='application/json')
    else:
        return render(request, 'find_blog_from_title_or_content.html')


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
            if father_comment_id:  # 回复评论
                father = Comment.objects.filter(id=father_comment_id).first()
                com.father = father
                com.ancestor = father.ancestor if father.ancestor else father
                blog.comment_quantity += 1
            com.save()
            blog.save()
            resp['success'] = 1
        else:
            resp['error'] = '请先登录后再评论'
        return HttpResponse(json.dumps(resp))


@csrf_exempt
def saying(request):
    say_list = []
    all_saying = Saying.objects.all().order_by('-say_time')
    for saying in all_saying:
        say_list.append(get_says_dict(saying))
    page = request.GET.get('page', 1)
    contacts = paging(say_list, 20, page)
    return render(request, 'moodList.html', {'all_saying': contacts})


def get_says_dict(saying):
    say_dict = {}
    say_dict['say_context'] = saying.say_context
    say_dict['say_time'] = str(saying.say_time).split('+')[0]
    say_dict['image'] = saying.image
    return say_dict


@csrf_exempt
def tag(request):
    tag_name = request.GET.get('tag_name', '')
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        all_blog = Tags.objects.get(tag=tag_name).blog_set.all().order_by('-blog_time')[(page - 1) * size:page * size]
        resp['success'] = 1
        for blog in all_blog:
            resp['data'].append(get_blog(blog))
        resp['total'] = Blog.objects.all().count()
        return HttpResponse(json.dumps(resp), content_type='application/json')
    else:
        return render(request, 'tag_article.html', {'tag_name': tag_name})


@login_required()
@csrf_exempt
def personal_center(request):
    resp = {'success': 0, 'error': ''}
    username = request.session.get('username', '')
    city = get_position(request)
    if request.method == 'POST':
        initial_pw = request.POST.get('initial_pw', '')
        new_pw = request.POST.get('new_pw', '')
        new_pw2 = request.POST.get('new_pw2', '')
        result = auth.authenticate(username=username, password=initial_pw)
        if result is None:
            resp['error'] = '原始密码输入错误'
        else:
            if not new_pw == new_pw2:
                resp['error'] = '两次密码输入不一致'
            else:
                user = User.objects.get(username=username)
                user.set_password(new_pw2)
                user.save()
                resp['success'] = 1
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'personal_center.html', {'username': username, 'city': city})


@csrf_exempt
def user_blog(request):
    author = request.GET.get('author', '')
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        all_blog = User.objects.get(username=author).blog_set.all().order_by('-blog_time')[
                   (page - 1) * size:page * size]
        resp['success'] = 1
        for blog in all_blog:
            resp['data'].append(get_blog(blog))
        resp['total'] = Blog.objects.all().count()
        return HttpResponse(json.dumps(resp), content_type='application/json')
    else:
        return render(request, 'user_blog.html', {'author': author})


@csrf_exempt
def msg_update(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        msg_author = request.session.get('username', '')
        msg_content = request.POST.get('msg_content', '')
        father_comment_id = request.POST.get('father_comment_id', '')
        if msg_author:
            username = User.objects.filter(username=msg_author).first()
            resp['success'] = 1
            msg = MesBoard(msg_author=username, msg_content=str(msg_content))
            if father_comment_id:  # 回复留言
                father = MesBoard.objects.filter(id=father_comment_id).first()
                msg.father = father
                msg.ancestor = father.ancestor if father.ancestor else father
            msg.save()
        else:
            resp['error'] = '请登录后再评论'
        return HttpResponse(json.dumps(resp))


@csrf_exempt
def msg_board(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        for msg in MesBoard.objects.filter(father__isnull=True).all().order_by('-msg_time')[
                   (page - 1) * size:page * size]:
            father_msg = get_msg_dict(msg)
            father_msg['children'] = []
            for child_msg in MesBoard.objects.filter(ancestor=msg).order_by('-msg_time'):
                father_msg['children'].append(get_msg_dict(child_msg))
            resp['data'].append(father_msg)
        resp['total'] = MesBoard.objects.filter(father__isnull=True).all().count()
        resp['success'] = 1
        return HttpResponse(json.dumps(resp))
    else:
        return render(request, 'message_board.html')


def get_msg_dict(msg):
    msg_att = {}
    msg_att['father'] = msg.father_id
    msg_att['father_name'] = msg.father.msg_author.username if msg.father else ''
    msg_att['msg_id'] = msg.id
    msg_att['msg_content'] = msg.msg_content
    msg_att['msg_author'] = msg.msg_author.username
    msg_att['msg_time'] = str(msg.msg_time).split('+')[0]
    return msg_att


def connect():
    url = 'https://news.sina.com.cn/china/'
    res = requests.get(url)
    # 使用UTF-8编码
    res.encoding = 'UTF-8'
    # 使用剖析器为html.parser
    soup = BeautifulSoup(res.text, 'html.parser')
    return soup


def search_news(request):
    search_content = request.GET.get('search_content', '')
    data = []
    for news in connect().select('li'):
        new = {}
        h2 = news.select('a')
        for i in h2:
            ss = i.text.encode("utf-8")
            if len(i.text) > 5 and not ss.replace(' ', '').strip().isalpha():
                pattern = re.compile('href=\"(.+?)\"')
                a = re.findall(pattern, str(i))
                new['title'] = ss
                new['content'] = a[0]
                if new:
                    if search_content:
                        if search_content in ss:
                            data.append(new)
                    else:
                        data = []
    page = request.GET.get('page', 1)
    contacts = paging(data, 20, page)

    return render(request, 'find_news_from_title.html',
                  {'news': contacts, 'search_content': search_content, 'len': len(data)})


def news_spider(request):
    data = []
    for news in connect().select('li'):
        new = {}
        h2 = news.select('a')
        for i in h2:
            ss = i.text.encode("utf-8")
            if len(i.text) > 5 and not ss.replace(' ', '').strip().isalpha():
                pattern = re.compile('href=\"(.+?)\"')
                a = re.findall(pattern, str(i))
                new['title'] = ss
                new['content'] = a[0]
                if new:
                    data.append(new)
    page = request.GET.get('page', 1)
    contacts = paging(data, 20, page)
    return render(request, 'news.html', {'news': contacts, 'len': -1})


def video(request, sort_type):
    video_list = []
    if int(sort_type) == 0:
        all_video = Video.objects.all().order_by('-upload_time')
        for a_video in all_video:
            a_video.video_size = get_video_dict(a_video, is_convert=False)['video_size']
            a_video.save()
            video_list.append(get_video_dict(a_video))
    elif int(sort_type) == 1:
        all_video = Video.objects.all().order_by('video_size')
        for a_video in all_video:
            video_list.append(get_video_dict(a_video))
    elif int(sort_type) == 2:
        all_video = Video.objects.all().order_by('-video_size')
        for a_video in all_video:
            video_list.append(get_video_dict(a_video))
    elif int(sort_type) == 3:
        all_video = Video.objects.all().order_by('upload_time')
        for a_video in all_video:
            video_list.append(get_video_dict(a_video))
    page = request.GET.get('page', 1)
    contacts = paging(video_list, 20, page)
    return render(request, 'all_video.html', {'all_video': contacts, 'len': -1})


@csrf_exempt
def video_detailed(request):
    resp = {'success': 0, 'error': '', 'data': []}
    video_title = request.GET.get('video_name', '')
    if request.method == 'POST':
        page = int(request.POST.get('page', 1))
        size = int(request.POST.get('size', 0))
        resp['success'] = 1
        resp['data'], total = get_video_comments(video_title, page, size)
        resp['total'] = total
        return HttpResponse(json.dumps(resp))
    else:
        video_attr = Video.objects.filter(video_title=video_title).first()
        get_video_dict(video_attr)
        return render(request, 'video_demo.html', {'video_dict': json.dumps(get_video_dict(video_attr))})


def get_video_dict(video_attr, is_convert=True):
    video_dict = {}
    video_size = VideoFileCheck('media/')
    if not is_convert:
        size = video_size.get_file_size(str(video_attr.video_path), is_convert=False)
    else:
        size = video_size.get_file_size(str(video_attr.video_path))
    video_dict['video_size'] = size
    video_dict['video_title'] = video_attr.video_title
    video_dict['upload_time'] = str(video_attr.upload_time).split('+')[0][0:10]
    video_dict['video_path'] = str(video_attr.video_path)
    video_dict['upload_user'] = video_attr.upload_user.username
    return video_dict


def get_music_dict(music):
    music_dict = {}
    music_dict['music_path'] = str(music.music_path)
    music_dict['upload_time'] = str(music.upload_time).split('+')[0][0:10]
    music_dict['music_title'] = music.music_title
    music_dict['singer'] = music.singer
    music_dict['upload_user'] = music.upload_user.username
    music_dict['lyric_path'] = str(music.lyric_path)
    return music_dict


def music(request):
    music_name = request.GET.get('music_name', '')
    music_attr = Music.objects.filter(music_title=music_name).first()
    get_music_dict(music_attr)
    with open('media/' + str(music_attr.lyric_path), 'r') as f:
        lyric = f.read()
    return render(request, 'mp3.html', {'music_attr': json.dumps(get_music_dict(music_attr)), 'lyric': lyric})


def all_music(request):
    music_list = []
    musics = Music.objects.all().order_by('-upload_time')
    for music in musics:
        music_list.append(get_music_dict(music))
    page = request.GET.get('page', 1)
    contacts = paging(music_list, 20, page)
    return render(request, 'all_mp3.html', {'all_music': contacts, 'len': -1})


def find_songs_from_singer(request):
    music_list = []
    singer = request.GET.get('singer', '')
    musics = Music.objects.filter(singer__icontains=singer).all().order_by('-upload_time')
    for music in musics:
        music_list.append(get_music_dict(music))
    page = request.GET.get('page', 1)
    contacts = paging(music_list, 20, page)
    return render(request, 'find_songs_from_singer.html',
                  {'all_music': contacts, 'singer': singer, 'len': len(music_list)})


def search_mus(request):
    music_list = []
    search_content = request.GET.get('search_content', '')
    if search_content:
        musics = Music.objects.filter(Q(singer__icontains=search_content) | Q(music_title__icontains=search_content))
        for music in musics:
            music_list.append(get_music_dict(music))
    else:
        music_list = []
    page = request.GET.get('page', 1)
    contacts = paging(music_list, 20, page)
    return render(request, 'find_songs_from_singer.html',
                  {'all_music': contacts, 'singer': search_content, 'len': len(music_list) if len(music_list) else 0})


def paging(afferent_list, num, page):
    paginator = Paginator(afferent_list, num)
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return contacts


def search_video(request, sort_type):
    video_list = []
    search_content = request.GET.get('search_content', '')
    if search_content:
        if int(sort_type) == 0:
            videos = Video.objects.filter(Q(video_title__icontains=search_content)).order_by('-upload_time')
        elif int(sort_type) == 1:
            videos = Video.objects.filter(Q(video_title__icontains=search_content)).order_by('video_size')
        elif int(sort_type) == 2:
            videos = Video.objects.filter(Q(video_title__icontains=search_content)).order_by('-video_size')
        elif int(sort_type) == 3:
            videos = Video.objects.filter(Q(video_title__icontains=search_content)).order_by('upload_time')
        for video in videos:
            video_list.append(get_video_dict(video))
    else:
        video_list = []
    page = request.GET.get('page', 1)
    contacts = paging(video_list, 20, page)
    return render(request, 'find_video_from_title.html',
                  {'all_video': contacts, 'video': search_content, 'len': len(video_list)})


def search_say(request):
    say_list = []
    search_content = request.GET.get('search_content', '')
    says = Saying.objects.filter(Q(say_context__icontains=search_content))
    for say in says:
        say_list.append(get_says_dict(say))
    page = request.GET.get('page', 1)
    contacts = paging(say_list, 20, page)
    return render(request, 'find_says_from_content.html',
                  {'all_saying': contacts, 'say': search_content, 'len': len(say_list)})


def get_video_com_dict(comment):
    comment_att = {}
    comment_att['father'] = comment.father_id
    comment_att['father_name'] = comment.father.comment_author.username if comment.father else ''
    comment_att['comment_id'] = comment.id
    comment_att['comment_content'] = comment.comment_content
    comment_att['comment_author'] = comment.comment_author.username
    comment_att['comment_time'] = str(comment.comment_time).split('+')[0]
    return comment_att


def get_video_comments(video_name='', page=1, size=5):
    result = []
    for comment in CommentVideo.objects.filter(video__video_title=video_name, father__isnull=True).order_by(
            '-comment_time')[(page - 1) * size:page * size]:
        father_dict = get_video_com_dict(comment)
        father_dict['children'] = []
        for child_com in CommentVideo.objects.filter(ancestor=comment).order_by('comment_time'):
            father_dict['children'].append(get_video_com_dict(child_com))
        result.append(father_dict)
    total = CommentVideo.objects.filter(video__video_title=video_name, father__isnull=True).count()
    return result, total


@csrf_exempt
def video_comment(request):
    resp = {'success': 0, 'error': '', 'data': []}
    if request.method == 'POST':
        comment_content = request.POST.get('comment_content')
        comment_author = request.session.get('username', '')
        father_comment_id = request.POST.get('father_comment_id', '')
        if comment_author:
            username = User.objects.filter(username=comment_author).first()
            video_title = request.POST.get('video_title')
            video = Video.objects.filter(video_title=video_title).first()
            com = CommentVideo(comment_author=username, comment_content=str(comment_content), video=video)
            if father_comment_id:  # 回复评论
                father = CommentVideo.objects.filter(id=father_comment_id).first()
                com.father = father
                com.ancestor = father.ancestor if father.ancestor else father
                # video.comment_quantity += 1
            com.save()
            video.save()
            resp['success'] = 1
        else:
            resp['error'] = '请先登录后再评论'
        return HttpResponse(json.dumps(resp))


def wangyi_head():
    url = 'http://c.m.163.com/nc/article/headline/T1348647853363/0-100.html'
    res = requests.get(url, headers=headers).text
    data = json.loads(res)
    return data


def wangyi_news(request, sort_type):
    news = wangyi_head()['T1348647853363']
    sort_news = []
    if int(sort_type) == 1:
        sort_news = sorted(news, key=lambda x: x['replyCount'])
    elif int(sort_type) == 2:
        sort_news = sorted(news, key=lambda x: x['replyCount'], reverse=True)
    elif int(sort_type) == 0:
        sort_news = sorted(news, key=lambda x: x['ptime'], reverse=True)
    elif int(sort_type) == 3:
        sort_news = sorted(news, key=lambda x: x['ptime'])
    page = request.GET.get('page', 1)
    contacts = paging(sort_news, 10, page)
    return render(request, 'wangyi_news.html', {'news': contacts, 'len': -1})


def search_wangyi_news(request, sort_type):
    search_content = request.GET.get('search_content', '')
    news = wangyi_head()['T1348647853363']
    data = []
    for new in news:
        new_dict = {}
        if search_content in new['title']:
            new_dict['title'] = new['title']
            new_dict['url_3w'] = new['url_3w'] if new['url_3w'] else "null"
            new_dict['ptime'] = new['ptime']
            new_dict['imgsrc'] = new['imgsrc']
            new_dict['replyCount'] = new['replyCount']
            data.append(new_dict)
    sort_news = []
    if int(sort_type) == 1:
        sort_news = sorted(data, key=lambda x: x['replyCount'])
    elif int(sort_type) == 2:
        sort_news = sorted(data, key=lambda x: x['replyCount'], reverse=True)
    elif int(sort_type) == 0:
        sort_news = sorted(data, key=lambda x: x['ptime'], reverse=True)
    elif int(sort_type) == 3:
        sort_news = sorted(data, key=lambda x: x['ptime'])
    page = request.GET.get('page', 1)
    contacts = paging(sort_news, 10, page)
    return render(request, 'find_wangyi_news_from_title.html', {'news': contacts, 'search_content': search_content, 'len': len(sort_news)})


def get_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    if ip == '' or ip is None:
        ip = request.META.get('HTTP_CLIENT_IP')
    if ip == "" or ip is None:
        ip = "X.X.X.X"
    return ip


def get_position(request):
    ip = get_ip(request)
    # url = "http://ip.taobao.com/service/getIpInfo.php?ip=203.100.83.38"
    url = "http://ip.taobao.com/service/getIpInfo.php?ip={}".format(ip)
    res = requests.get(url, headers=headers).text
    city = json.loads(res)['data']['city']
    return city


def weather_forecast(request):
    return render(request, 'weather_forecast.html')

