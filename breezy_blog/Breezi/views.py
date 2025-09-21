from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import UserRegisterForm, PostForm
from .models import Post

def post_list(request):
    posts = Post.objects.filter(is_published=True)
    return render(request, "Breezi/post_list.html", {"posts": posts})

def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not post.is_published and post.author != request.user:
        return render(request, "404.html", status=404)
    return render(request, "Breezi/post_detail.html", {"post": post})

@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            p.save()
            messages.success(request, "Post created!")
            return redirect("post_detail", pk=p.pk)
    else:
        form = PostForm()
    return render(request, "Breezi/post_form.html", {"form": form, "action": "Create"})

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "Not allowed.")
        return redirect("post_detail", pk=pk)
    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "Breezi/post_form.html", {"form": form, "action": "Edit"})

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "Not allowed.")
        return redirect("post_detail", pk=pk)
    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("post_list")
    return render(request, "Breezi/post_confirm_delete.html", {"post": post})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Welcome!")
            return redirect("post_list")
    else:
        form = UserRegisterForm()
    return render(request, "Breezi/register.html", {"form": form})
