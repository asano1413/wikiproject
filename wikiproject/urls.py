from django.urls import path
from django.contrib.auth import views as auth_views
from wikiapp import views
from django.contrib import admin
from django.conf.urls.static import static

from wikiapp.views import content_view
from wikiproject import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/<int:pk>/add_comment/', views.add_comment, name='add_comment'),
    path('create/', views.create_post, name='create_post'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('add_comment/', views.add_comment, name='add_comment'),
    path('content1/',views.content_view,name="content_view"),
    path('tag/<str:tag_name>/', views.tag_content_list, name='tag_content_list'),
    path('tags/', views.tag_list, name='tag_list'),
    path('profile/',views.profile_view, name='profile_view'),
    path('<int:post_id>', views.toggle_like, name='toggle_like'),
    path('post/<int:pk>/delete/', views.delete_post, name='delete_post'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('logout/', views.logout_view, name='logout'),
    path('search/',views.search_view, name='search'),
    path('contact/',views.contact_view, name='contact'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)