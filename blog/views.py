from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from .models import Blog,BlogType
from read_statistics.utils import read_statistics_once_read
from comment.models import Comment
from .forms import PostForm
from comment.forms import CommentForm
# Create your views here.
# 
def get_blog_list_common_data(request,blogs_all_list):
    paginator=Paginator(blogs_all_list,settings.EACH_PAGE_NUMBER)#每页10篇
    page_num = request.GET.get('page', 1)  # 获取url的页面参数（GET请求)
    page_of_blogs=paginator.get_page(page_num)
    page_range=[x for x in range(int(page_num)-2,int(page_num)+3) if 0<x<=paginator.num_pages]#用于显示页面的前后两页

    #加上省略页码标记
    if page_range[0]-1>=2:
        page_range.insert(0,'...')
    if paginator.num_pages - page_range[-1] >=2:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0,1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类的对应博客的数量
    '''blog_types=BlogType.objects.all()
    blog_types_list=[]
    for blog_type in blog_types:
        blog_type.blog_count=Blog.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
        以上是一种获取的方法
    '''

    #获取日期归档对应的博客数量
    blog_dates=Blog.objects.dates('created_time','month',order='DESC')
    blog_dates_dict={}
    for blog_date in blog_dates:
        blog_count=Blog.objects.filter(created_time__year=blog_date.year,
                                        created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date]=blog_count
    

    context={}
    context['page_of_blogs']=page_of_blogs
    context['page_range']=page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))#这里的blog是models下的Blogtype关联类名的小写
    context['blog_dates']=blog_dates_dict
    context['post_form']=PostForm()
    return context

def blog_list(request):

    blogs_all_list=Blog.objects.all()
    context=get_blog_list_common_data(request,blogs_all_list)
    return render(request,'blog/blog_list.html',context)

def blogs_type_with(request,blogs_type_with):
    blogs_all_list=Blog.objects.filter(blog_type=blogs_type_with)
    context=get_blog_list_common_data(request,blogs_all_list)
    blog_type=get_object_or_404(BlogType,pk=blogs_type_with)
    context['blog_type'] = blog_type
    return render(request,'blog/blogs_type_with.html',context)

def blogs_with_date(request,year,month):
    blogs_all_list=Blog.objects.filter(created_time__year=year , created_time__month=month )
    context=get_blog_list_common_data(request,blogs_all_list)
    context['blogs_with_date']='%s年%s月' % (year,month)
    return render(request,'blog/blogs_with_date.html',context)

def blog_detail(request,blog_pk):
    blog=get_object_or_404(Blog,pk=blog_pk)
    read_cookie_key=read_statistics_once_read(request, blog)
    context={}
    
    context['previous_blog']=Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog']=Blog.objects.filter(created_time__lt=blog.created_time).first()
    # 这里的__gt和__lt表示大于等于和小于等于，这里用created_time作为标准而不是id是因为当一些博客被删除后，
    # 其id也会占着位置，导致出错，所以用created_time比较好
    context['blog']=blog
    response = render(request,'blog/blog_detail.html',context) #响应
    response.set_cookie(read_cookie_key, 'true')#阅读cookie标记
    return response


def update_post(request):
    '''referer = request.META.get('HTTP_REFERER',reverse('home'))
    if not request.user.is_authenticated:
        return render(request, 'error.html',{'message':'用户未登录','redirect_to':referer})
    title = request.POST.get('title','').strip()
    if title == '':
        return render(request, 'error.html',{'message':'标题不能为空','redirect_to':referer})
    content = request.POST.get('content','').strip()
    if content == '':
        return render(request, 'error.html',{'message':'内容不能为空','redirect_to':referer})
    blog_type = request.POST.get('blog_type','')
    if blog_type == '':
        return render(request, 'error.html',{'message':'类型不能为空','redirect_to':referer})

    blog = Blog()
    blog.title = title
    blog.content = content
    blog.author = request.user
    blog.blog_type = get_object_or_404(BlogType,type_name=blog_type)
    blog.save()

    
    return redirect(referer)
    '''
    referer = request.META.get('HTTP_REFERER', reverse('home'))

    post_form = PostForm(request.POST, user=request.user)
    blog = Blog()
    blog_type = request.POST.get('blog_type','')
    data={}
    if blog_type == '':
        return render(request, 'error.html',{'message':'类型不能为空','redirect_to':referer})
    
    blog.blog_type = get_object_or_404(BlogType,type_name=blog_type)
    blog.author = request.user
    if post_form.is_valid():
        blog.title = post_form.cleaned_data['title']
        blog.content = post_form.cleaned_data['text']
        blog.save()
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
        data['message'] = list(post_form.errors.value())[0][0]

    return redirect(referer)