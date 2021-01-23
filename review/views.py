from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http  import HttpResponse,Http404
from .models import Project,Profile,Rating
from django.db.models import Avg
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render,redirect,get_object_or_404
from .forms import UpdateUserForm,UpdateUserProfileForm,NewPostForm,ProjectRatingForm


from rest_framework.response import Response
from rest_framework.views import APIView

from .serializer import MerchSerializer,MerchSerializer1
from rest_framework import status

class MerchList(APIView):
    def get(self, request, format=None):
        all_merch = Profile.objects.all()
        serializers = MerchSerializer(all_merch, many=True)
        return Response(serializers.data)


    def post(self, request, format=None):
        serializers = MerchSerializer(data=request.data)
        if serializers.is_valid():
            serializers.save()
            return Response(serializers.data, status=status.HTTP_201_CREATED)
        return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)    

class MerchList2(APIView):
    def get(self, request, format=None):
        all_merch = Project.objects.all()
        serializers = MerchSerializer1(all_merch, many=True)
        return Response(serializers.data)

# Create your views here.
@login_required(login_url='/accounts/login/')
def landing(request):
    
    posts = Project.objects.all().order_by('-date_posted')
    users = User.objects.exclude(id=request.user.id)
    current_user = request.user
    
    return render(request,"awwards/landing.html",{'posts':posts,'user':current_user,'users':users})



@login_required(login_url='/accounts/login')
def profile(request):
    posts = Project.objects.all().order_by('-date_posted')
    
    return render(request, 'awwards/profile.html', {'posts':posts})
@login_required(login_url='/accounts/login/')
def edit(request):
    
    
    if request.method == "POST":
        user_form = UpdateUserForm(request.POST, instance=request.user)
        prof_form = UpdateUserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and prof_form.is_valid():
            user_form.save()
            prof_form.save()
            return redirect('profile')
            # return HttpResponseRedirect(request.path_info)
    else:
        user_form = UpdateUserForm(instance=request.user)
        prof_form = UpdateUserProfileForm(instance=request.user.profile)

    params = {
        # 'images' : images,   
        'user_form': user_form,
        'prof_form': prof_form,
        
    }
    return render(request, 'new_profile.html', params )

@login_required(login_url='/accounts/login/')
def new_post(request):
    current_user = request.user
    if request.method == 'POST':
        form = NewPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = current_user
            post.save()
        return redirect('landing')
    else:
        form = NewPostForm()
    return render(request, 'newpost.html', {"form": form})

def single_project(request, c_id):
    current_user = request.user
    current_project = Project.objects.get(id=c_id)
    ratings = Rating.objects.filter(post_id=c_id)
    usability = Rating.objects.filter(post_id=c_id).aggregate(Avg('usability_rating'))
    content = Rating.objects.filter(post_id=c_id).aggregate(Avg('content_rating'))
    design = Rating.objects.filter(post_id=c_id).aggregate(Avg('design_rating'))

    return render(request, 'project.html',
                  {"project": current_project, "user": current_user, 'ratings': ratings, "design": design,
                   "content": content, "usability": usability})
def review_rating(request, id):
    current_user = request.user

    current_project = Project.objects.get(id=id)

    if request.method == 'POST':
        form = ProjectRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.project = current_project
            rating.user = current_user
            rating.save()
            return redirect('project', id)
    else:
        form = ProjectRatingForm()

    return render(request, 'rating.html', {'form': form, "project": current_project, "user": current_user})

def search_results(request):
    if 'projects' in request.GET and request.GET['projects']:
        search_term = request.GET.get("projects")
        searched_projects = Project.search_by_name(search_term)
        
        message = f'{search_term}'
        
        return render(request,'search.html',{"message":message,"posts":searched_projects})
    
    else:
        message = "You haven't searched for any term"
        return render(request,'search.html',{"message":message,"posts":searched_projects})
    
