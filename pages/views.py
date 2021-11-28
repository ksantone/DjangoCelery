from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
#from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
#from datasets.models import Dataset
from django.core.paginator import Paginator

# Create your views here.
from .models import *
from .forms import CreateUserForm

def home_page_view(request, *args, **kwargs):
	return render(request, "home.html", {})

'''def my_data_view(request, *args, **kwargs):
	datasets = Dataset.objects.all()
	context = {
		"datasets": datasets
	}
	return render(request, "mydata.html", context)

def my_datasets_view(request, *args, **kwargs):
	datasets = Dataset.objects.all()
	paginated_datasets = Paginator(datasets, 3)
	page_number = request.GET.get('page', 1)
	page = paginated_datasets.get_page(page_number)
	if page.has_next():
		next_url = f'?page={page.next_page_number()}'
	else:
		next_url = ''
	if page.has_previous():
		prev_url = f'?page={page.previous_page_number()}'
	else:
		prev_url = ''
	context = {
		"datasets": page,
		"next_page_url": next_url,
		"prev_page_url": prev_url
	}
	return render(request, "mydatasets.html", context)'''

def search_results_view(request):
	search_query = request.GET.get('search', '')
	context = {}
	'''if search_query:
		datasets = Dataset.objects.filter(title__icontains=search_query)
		paginated_datasets = Paginator(datasets, 5)
		page_number = request.GET.get('page', 1)
		page = paginated_datasets.get_page(page_number)
		if page.has_next():
			next_url = f'?page={page.next_page_number()}'
		else:
			next_url = ''
		if page.has_previous():
			prev_url = f'?page={page.previous_page_number()}'
		else:
			prev_url = ''
		context['datasets'] = page
		context['search_query'] = search_query'''
	return render(request, "search_results.html", context)

def register_page_view(request, *args, **kwargs):
	form = CreateUserForm()
	if request.method == "POST":
		form = CreateUserForm(request.POST)
		if form.is_valid():
			form.save()
			user = form.cleaned_data.get('username')
			messages.success(request, 'Account was created for ' + user)
			return redirect(login_page_view)
	context = {
		"form": form
	}
	return render(request, "register.html", context)

def login_page_view(request, *args, **kwargs):
	context = {}
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			login(request, user)
			return redirect(home_page_view)
		else:
			messages.info(request, 'Username OR password is incorrect.')
	return render(request, "login.html", context)

def logout_page_view(request, *args, **kwargs):
	logout(request)
	return redirect(home_page_view)