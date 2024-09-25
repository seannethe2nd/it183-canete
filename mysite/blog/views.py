from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import BlogPost, Review
from .forms import ReviewForm, BlogPost
from .forms import UserRegisterForm, BlogPostForm
from django.db.models import Avg, Count


def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Automatically log the user in after registration
            return redirect('blog_list')  # Redirect to the blog list page after registration
    else:
        form = UserRegisterForm()
    return render(request, 'blog/register.html', {'form': form})
    

@login_required
def blog_list(request):
    # Determine if the user wants to filter posts
    filter_type = request.GET.get('filter', 'all')

    # Filter posts accordingly
    if filter_type == 'my_posts':
        posts = BlogPost.objects.filter(author=request.user).annotate(avg_rating=Avg('reviews__rating'))
    else:
        posts = BlogPost.objects.all().annotate(avg_rating=Avg('reviews__rating'))

    # Handle blog post creation (if POST request)
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            blog_post = form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()
            return redirect('blog_list')
    else:
        form = BlogPostForm()

    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'form': form,
        'filter_type': filter_type
    })


def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    reviews = post.reviews.all()

    # Calculate the number of reviews for each star rating (1 to 5 stars)
    review_tally = reviews.values('rating').annotate(star_count=Count('rating')).order_by('-rating')

    # Total number of reviews
    total_reviews = reviews.count()

    # Calculate the average rating
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating is not None:
        average_rating = round(average_rating, 1)  # Round to 1 decimal place

    # Calculate the percentage for each rating (used for progress bars)
    for tally in review_tally:
        tally['percentage'] = (tally['star_count'] / total_reviews) * 100 if total_reviews > 0 else 0

    # Handle review submission
    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.reviewer = request.user
                review.blog_post = post
                review.save()
                return redirect('blog_detail', pk=post.pk)
        else:
            return redirect('login')  # Redirect to login if the user is not authenticated
    else:
        form = ReviewForm()

    context = {
        'post': post,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'review_tally': review_tally,
        'average_rating': average_rating,
        'form': form,
    }
    
    return render(request, 'blog/blog_detail.html', context)



def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('blog_list')
        else:
            return render(request, 'blog/login.html', {'error': 'Invalid credentials'})
    return render(request, 'blog/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')


# My Posts view (list posts created by the user)
@login_required
def my_posts(request):
    posts = BlogPost.objects.filter(author=request.user)
    return render(request, 'blog/my_posts.html', {'posts': posts})

# Edit Post view
@login_required
def edit_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('my_posts')
    else:
        form = BlogPostForm(instance=post)
    return render(request, 'blog/edit_post.html', {'form': form, 'post': post})

# Delete Post view
@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('my_posts')
    return render(request, 'blog/delete_post.html', {'post': post})