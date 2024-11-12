from django.db import models
from django.contrib.auth.models import User

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    main_image = models.ImageField(upload_to='blog_images/', blank=True, null=True)

    def __str__(self):
        return self.title

    @property
    def like_count(self):
        return self.likes.count()
        
class Review(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='reviews', on_delete=models.CASCADE)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.blog_post.title} by {self.reviewer.username}'

class Like(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('blog_post', 'user')
class GalleryImage(models.Model):
    blog_post = models.ForeignKey(BlogPost, related_name='gallery_images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog_post_images/')
    caption = models.CharField(max_length=200, blank=True)

    def save(self, *args, **kwargs):
        if not self.caption:
            # Count existing images for this blog post to generate a unique number
            image_count = GalleryImage.objects.filter(blog_post=self.blog_post).count() + 1
            # Use image filename as part of the default caption
            filename = self.image.name.split('/')[-1]  # Get just the file name, not the path
            self.caption = f"{filename} #{image_count}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.blog_post.title}"
