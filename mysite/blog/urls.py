from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('post/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),  # Registration URL
    path('my-posts/', views.my_posts, name='my_posts'),
    path('edit-post/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete-post/<int:pk>/', views.delete_post, name='delete_post'),
    path('blog/<int:post_id>/toggle-like/', views.toggle_like, name='toggle_like'),
    path('post/gallery_image/<int:image_pk>/remove/', views.remove_gallery_image, name='remove_gallery_image'),

]
