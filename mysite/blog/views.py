from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import BlogPost, Review, Like, GalleryImage
from .forms import ReviewForm, BlogPost
from .forms import UserRegisterForm, BlogPostForm, GalleryImageForm, GalleryImageFormSet
from django.db.models import Avg, Count
from django.http import JsonResponse


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
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'my_posts':
        posts = BlogPost.objects.filter(author=request.user).annotate(avg_rating=Avg('reviews__rating'))
    else:
        posts = BlogPost.objects.all().annotate(avg_rating=Avg('reviews__rating'))

    if request.method == 'POST':
        blog_post_form = BlogPostForm(request.POST, request.FILES)  # Main blog post form
        gallery_image_formset = GalleryImageFormSet(request.POST, request.FILES, queryset=GalleryImage.objects.none())

        if blog_post_form.is_valid() and gallery_image_formset.is_valid():
            # Save the blog post first
            blog_post = blog_post_form.save(commit=False)
            blog_post.author = request.user
            blog_post.save()

            # Save gallery images
            for form in gallery_image_formset:
                if form.cleaned_data.get('image'):
                    gallery_image = form.save(commit=False)
                    gallery_image.blog_post = blog_post
                    gallery_image.save()

            return redirect('blog_list')
    else:
        blog_post_form = BlogPostForm()
        gallery_image_formset = GalleryImageFormSet(queryset=GalleryImage.objects.none())

    return render(request, 'blog/blog_list.html', {
        'posts': posts,
        'blog_post_form': blog_post_form,
        'gallery_image_formset': gallery_image_formset,
        'filter_type': filter_type
    })

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    reviews = post.reviews.all()
    user_has_liked = post.likes.filter(user=request.user).exists() if request.user.is_authenticated else False

    # Calculate the number of reviews for each star rating (1 to 5 stars)
    review_tally = reviews.values('rating').annotate(star_count=Count('rating')).order_by('-rating')
    total_reviews = reviews.count()
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    if average_rating is not None:
        average_rating = round(average_rating, 1)

    for tally in review_tally:
        tally['percentage'] = (tally['star_count'] / total_reviews) * 100 if total_reviews > 0 else 0

    if request.method == 'POST' and 'review_form' in request.POST:
        form = ReviewForm(request.POST)
        if form.is_valid() and request.user.is_authenticated:
            review = form.save(commit=False)
            review.reviewer = request.user
            review.blog_post = post
            review.save()
            return redirect('blog_detail', pk=post.pk)
    else:
        form = ReviewForm()

    context = {
        'post': post,
        'reviews': reviews,
        'total_reviews': total_reviews,
        'review_tally': review_tally,
        'average_rating': average_rating,
        'form': form,
        'user_has_liked': user_has_liked,
        'like_count': post.like_count,
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
    gallery_images = GalleryImage.objects.filter(blog_post=post)  # Retrieve existing gallery images

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        
        if form.is_valid():
            form.save()

            # Handling new gallery images
            gallery_images_files = request.FILES.getlist('gallery_images')
            for image_file in gallery_images_files:
                GalleryImage.objects.create(blog_post=post, image=image_file)

            return redirect('my_posts')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/edit_post.html', {
        'form': form,
        'post': post,
        'gallery_images': gallery_images,
    })

@login_required
def remove_gallery_image(request, image_pk):
    image = get_object_or_404(GalleryImage, pk=image_pk, blog_post__author=request.user)
    image.delete()
    return redirect('edit_post', pk=image.blog_post.pk)

# Delete Post view
@login_required
def delete_post(request, pk):
    post = get_object_or_404(BlogPost, pk=pk, author=request.user)
    if request.method == 'POST':
        post.delete()
        return redirect('my_posts')
    return render(request, 'blog/delete_post.html', {'post': post})

@login_required
def toggle_like(request, post_id):
    if request.method == "POST":
        blog_post = get_object_or_404(BlogPost, id=post_id)
        user = request.user

        like, created = Like.objects.get_or_create(blog_post=blog_post, user=user)
        if not created:
            like.delete()
            return JsonResponse({'message': 'Like removed', 'like_count': blog_post.like_count}, status=200)

        return JsonResponse({'message': 'Like added', 'like_count': blog_post.like_count}, status=201)

    return JsonResponse({'error': 'Invalid request'}, status=400)