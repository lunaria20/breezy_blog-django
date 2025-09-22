from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login as auth_login
from .forms import UserRegisterForm, PostForm
from .models import Post


# --- Static Pages ---
def about(request):
    return render(request, "Breezi/about.html")


def contact(request):
    return render(request, "Breezi/contact.html")


def test_page(request):
    return render(request, "Breezi/test.html")


# --- Blog Views ---
def post_list(request):
    if request.user.is_authenticated:
        # Show published posts + drafts authored by the user
        posts = Post.objects.filter(is_published=True) | Post.objects.filter(author=request.user)
    else:
        posts = Post.objects.filter(is_published=True)

    posts = posts.order_by("-created_at")
    return render(request, "Breezi/post_list.html", {"posts": posts})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if not post.is_published and post.author != request.user:
        return render(request, "Breezi/404.html", status=404)  # Safe fallback
    return render(request, "Breezi/post_detail.html", {"post": post})


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.author = request.user
            p.is_published = True  # Auto-publish new posts
            p.save()
            messages.success(request, "Post created successfully!")
            return redirect("post_detail", pk=p.pk)
    else:
        form = PostForm()
    return render(request, "Breezi/post_form.html", {"form": form, "action": "Create"})


@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You are not allowed to edit this post.")
        return redirect("post_detail", pk=pk)

    if request.method == "POST":
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Post updated successfully!")
            return redirect("post_detail", pk=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, "Breezi/post_form.html", {"form": form, "action": "Edit"})


@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        messages.error(request, "You are not allowed to delete this post.")
        return redirect("post_detail", pk=pk)

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted.")
        return redirect("home")  # Redirect to home after delete
    return render(request, "Breezi/post_confirm_delete.html", {"post": post})


# --- Auth Views ---
def register(request):
    if request.user.is_authenticated:
        # Already logged in → redirect to home
        messages.info(request, "You are already registered and logged in.")
        return redirect("home")

    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log user in immediately
            messages.success(request, f"Welcome, {user.username}! 🎉 Your account has been created.")
            return redirect("home")  # Go to homepage after registering
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, "Breezi/register.html", {"form": form})
