from multiprocessing import context
from unicodedata import category
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from rango.models import Category, Page
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order by # of likes in descending order
    # Retrieve top 5 only
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    
    # Construct a dictionary to pass to the template engine as its content
    # Note the key boldmessage matches to {{ boldmessage }} in the template
    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    context_dict['pages'] = page_list
    

    # return a rendered response to send to the client
    # we make use of the shortcut function to make our lives easier
    # not that the first parameter is the template we wish to use
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If not, get() will raise a DoesNotExist exception
        # get() returns one model instance or raises an exception
        category = Category.objects.get(slug=category_name_slug)
        # Retrieve all of the associated pages
        # filter returns a list of page objects or empty list
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        # we also add the category object from the db to the context dict
        # We'll use this in the template to verify that the category exists
        context_dict['category'] = category
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)


@login_required
def add_category(request):
    form = CategoryForm()
    
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # save the category to the db
            cat = form.save(commit=True)
            print(cat, cat.slug)
            # redirect user back to the index view
            return redirect('/rango/')
        else:
            print(form.errors)
    
    # render the form 
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except:
        category = None

    if category is None:
        return redirect('/rango/')
    
    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug':
                                                category_name_slug}))
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            profile = profile_form.save(commit=False)
            profile.user = user
            
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
        
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(request,
                'rango/register.html',
                context = {'user_form': user_form,
                            'profile_form': profile_form,
                            'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")

    else:
        return render(request, 'rango/login.html')


@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')
    # return HttpResponse("Since you're logged in, you can see this text!")


@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))

