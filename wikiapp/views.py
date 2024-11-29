from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from . import models
from .forms import PostForm, CommentForm, ProfileForm, ContactForm, SearchForm
from .models import Post, Tag, Like, Article, ContactEmail, Search


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('index')
            else:
                return HttpResponse("Invalid login")

    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def index(request):
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        if post_id:
            post = get_object_or_404(Post, pk=post_id)
            post.delete()
    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'index.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('/')
    else:
        form = PostForm()
    return render(request, 'post.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')

    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})

def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.save()
            return redirect('index')
        else:
            return render(request, 'comment_form.html', {'form': form})
    else:
#         POSTメソッドじゃない場合の処理
        form = CommentForm()
        return render(request, 'comment_form.html', {'form': form})

def content_view(request):
    content1_posts = Post.objects.filter(tag='content1').order_by('-created_at')[:3]
    content2_posts = Post.objects.filter(tag='content2').order_by('-created_at')[:3]
    content3_posts = Post.objects.filter(tag='content3').order_by('-created_at')[:3]
    context = {
        'content1_posts': content1_posts,
        'content2_posts': content2_posts,
        'content3_posts': content3_posts,
    }
    return render(request, 'content1.html', context)

def tag_content_list(request, tag_name):
    tag = get_object_or_404(Tag, name=tag_name)
    contents = tag.contents.all()
    return render(request, 'content1.html', {'tag': tag, 'contents': contents})

def tag_list(request):
    tags = Tag.objects.all()
    return render(request, 'tag_list.html', {'tags': tags})
def profile_view(request):
    def edit_profile(request):
        profile = request.user.profile
        if request.method == 'POST':
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            if form.is_valid():
                form.save()
                return redirect('profile')
        else:
            form = ProfileForm(instance=profile)
        return render(request, 'edit_profile.html', {'form': form})
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'profile.html', {'posts': posts})


def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()

    return redirect('/', post_id=post.id)

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.all()

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })

def search_view(request):
    results = None
    if request.method == 'GET':
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Search.objects.filter(title__icontains=query)
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form, 'results': results})

def posts_by_tags(request, tag_name):
    posts = Post.objects.filter(tags=tag_name).order_by('-created_at')   #タグ名でフィルタリングをかける
    if tag_name == '勉強用':
        template = 'content1.html'
    elif tag_name == 'ゲーム':
        template = 'content2.html'
    elif tag_name == '雑多':
        template = 'content3.html'
    else:
        return render(request,'404.html',status=404)

    context = {
        'posts': posts,
        'tag_name': tag_name
    }
    return render(request, template, context=context)

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # フォームからデータを取得
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # 送り元のメールアドレスをデータベースから取得
            try:
                sender_email = ContactEmail.objects.first().email  # 例: 最初のメールアドレスを取得
            except AttributeError:
                return HttpResponse("送り元メールアドレスが設定されていません。")

            # メールを送信
            try:
                send_mail(
                    subject,
                    message,
                    sender_email,  # 送り元
                    ['recipient@example.com'],  # 受信者
                )
                return HttpResponse("メールが送信されました！")
            except Exception as e:
                return HttpResponse(f"メールの送信に失敗しました: {e}")
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})

def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user != post.author:
        return HttpResponseForbidden("この投稿を削除する権限がありません。")
    if request.method == 'POST':
        post.delete()
        return redirect('index')
    return render(request, 'index.html', {'post': post})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('index')
    else:
        logout(request)
        return redirect('index')