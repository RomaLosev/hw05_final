from django.forms.utils import to_current_timezone
from django.shortcuts import render, get_object_or_404, redirect
from yatube.settings import PAGINATOR_PAGES
from posts.models import Post, Group, User, Follow
from posts.forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def index(request):

    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = 'Последние обновления на сайте'
    context = {
        'page_obj': page_obj,
        'title': title,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    title = f'Записи сообщества - {str(group)}'
    paginator = Paginator(posts, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'title': title,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    posts_count = post_list.count()
    paginator = Paginator(post_list, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(user=request.user,
                                          author=author).exists()
    context = {
        'page_obj': page_obj,
        'posts_count': posts_count,
        'author': author,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    group = post.group
    comments = post.comments.all()
    posts_count = post.author.posts.count()
    form = CommentForm()

    context = {
        'post': post,
        'author': author,
        'group': group,
        'posts_count': posts_count,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@csrf_exempt
@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    all_groups = Group.objects.all()
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'form': form, 'all_groups': all_groups}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.pub_date = to_current_timezone
    post.save()
    return redirect('posts:profile', username=post.author)


@csrf_exempt
@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    all_groups = Group.objects.all()
    is_edit = True
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {
            'post': post,
            'all_groups': all_groups,
            'is_edit': is_edit,
            'form': form
        })
    form = form.save(False)
    form.author = request.user
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if not form.is_valid():
        return redirect('posts:post_detail', post_id=post_id)
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user
    ).select_related('author', 'group')
    paginator = Paginator(post_list, PAGINATOR_PAGES)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
@csrf_exempt
def profile_follow(request, username):
    if request.user.username == username:
        return redirect('posts:profile', username=username)
    author = get_object_or_404(User, username=username)
    Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
@csrf_exempt
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if Follow.objects.filter(
        user=request.user,
        author=author
    ).exists():
        Follow.objects.filter(
            user=request.user,
            author=author
        ).delete()
    return redirect('posts:profile', username=username)
