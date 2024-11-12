from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BlogPost, GalleryImage

@receiver(post_save, sender=BlogPost)
def add_main_image_to_gallery(sender, instance, created, **kwargs):
    if created and instance.main_image:
        # Check if a GalleryImage for the main image already exists
        if not GalleryImage.objects.filter(blog_post=instance, image=instance.main_image).exists():
            # Create a GalleryImage entry with the main image
            GalleryImage.objects.create(blog_post=instance, image=instance.main_image, caption="Main Image")
