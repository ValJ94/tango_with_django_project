from multiprocessing import context
from unicodedata import category
from django.shortcuts import render
from django.http import HttpResponse
from rango.models import Category
from rango.models import Page

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
