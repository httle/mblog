from django.urls import path
from . import views

urlpatterns=[
    path('',views.blog_list,name='blog_list'),
    path('update_post/',views.update_post,name='update_post'),
    path('<int:blog_pk>',views.blog_detail,name="blog_detail"),
    path('blog/<int:blogs_type_with>',views.blogs_type_with,name='blogs_type_with'),
    path('blog/<int:year>/<int:month>',views.blogs_with_date,name='blogs_with_date'),
]