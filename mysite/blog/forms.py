from django import forms
from .models import Review, BlogPost, GalleryImage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        help_texts = {
                'username': None,
                'email': None,
                'password1': None,
                'password2': None
            }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Suppress help text
        for field_name in ['password1', 'password2']:
            self.fields[field_name].help_text = None  # Remove help text from password fields

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'main_image']  # Include the main image field

class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image', 'caption']

# Create a formset for GalleryImageForm
GalleryImageFormSet = modelformset_factory(GalleryImage, form=GalleryImageForm, extra=3)  # Set 'extra' to how many images you'd like to display initially

