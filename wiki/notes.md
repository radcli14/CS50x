# CS50W Lecture 3 Notes

## HTTP
- Hypertext transfer protocol
- Response is 
  * HTTP/<version> <code> OK, like `HTTP/1.1 200 Ok`
  * `content type: text/html`

## Django Startup
- `pip3 install Django`
- `django-admin startproject PROJECT_NAME` will create a set of template files
  * `manage.py` is created automatically, generally not touched, allows us to use and manage files
  * `settings.py` might be changed to add features or modify behaviours
  * `urls.py` which is like a table of contents
- `python manage.py runserver` will allow us to view
- `python manage.py startapp APP_NAME` will create a new app
  * After creating, need to go to `settings.py` and add to our `installed_apps` list

## Creating a View
- Need to add a function to `views.py` to create our view, and a response to a user request, for example:
```python
from django.http import HttpResponse

def index(request):
    return HttpResponse("hello world")
```
- In `urls.py` we will define the routes to our views 
```python
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index")
]
```
- need to define one for our app, as well as one for the whole project, this is what the project `urls.py` would look like
```python
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("APP_NAME/", include("APP_NAME.urls"))
]
```

## Adding Parameters
- Can parameterize the path by adding an additional parameter
```python
def greet(request, name):
    return HttpResponse(f"Hello, {name}")
```
- In the `urls.py` file, we could reach this with
```python
path("<str:name>", views.greet, name="greet")
```
- Render function can provide a response from an HTML template file (third argument is context)
```python
from django.shortcuts import render

def index(request, name):
    return render(request, "APP_NAME/greet.html", {
        "name": name.capitalize()
    })
```
- Inside `greet.html`
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Hello</title>
    </head>
    <body>
        <h1>Hello {{ name }}</h1>
    </body>
</html>
```
- Conditionals in template HTML
```html
{% if conditional %}
    <h1>YES</h1>
{% else %}
    <h1>NO</h1>
{% endif %}
```

## Static Files
- Files that don't change, like CSS
- Rather than hardcoding a URL, it is better to use this `<head>` syntax to link static files:
```html
<link href="{% static 'APP_NAME/styles.css' %}" rel="stylesheet">
```

## Loop Syntax
- Can add the `empty` condition to display content to help the user if nothing exists
```html
<ul>
    {% for task in tasks %}
        <li>{{ task }}</li>
    {% empty %}
        <li>Your list is empty!</li>
    {% endfor %}
</ul>
```

## Template Inheritance
- Create a layout file, for structure that is shared between pages
- Write placeholders for content that differs
```html
<!DOCTYPE html>
<html lang="en">
    <head>
        <title>Tasks</title>
    </head>
    <body>
        {% block body %}
        {% endblock %}
    </body>
</html>
```
- Inside your other html files
```html
{% extends "tasks/layout.html" %}

{% block body %}
    <h1>HTML specific to this page's body</h1>
{% endblock %}
```

## Linking to Named Routes
- Instead of hard-coding the URL as entered in the browser, in Django we can use the route name from `urls.py`
```html
<a href="{url 'add'}">Add a New Task</a>
```

## Namespace Collisions
- Issue where you have multiple apps in one project, you can have multiple routes named `index`, for example
- Inside the `urls.py` for a single app, need to add the app name
```python
app_name = "tasks"
```
- Then, when linking in HTML, reference that name
```html
<a href="{url 'tasks:index'}">View Tasks</a>
```

## Forms
- Add the URL link and method inside a form
- Post is used for modifying state, does not include parameters in the URL itself
```html
<form action="{% url 'tasks:add' %}" method="post">
```

### CSRF Cookies
- CSRF (Cross-site Request Forgery) cookies will be required by Django when using post requests
- Generated and stored in the session for each individual user
- Django Middleware add-on refers to the ability for Django to intervene in a request
- `settings.py` includes these MIDDLEWARE definitions
- To use this security feature, inside our form with the post request
```html
<form action="{% url 'tasks:add' %}" method="post">
    {% csrf_token %}
</form>
```

### Creating Forms Programmatically
- In our `views.py`, we can define Python code to generate a form, and add it to the context we provide to HTML
- Django forms can do client-side validation to intervene when submitting, such as the min and max values in the integer field below
```python
from django import forms

class NewTaskForm(forms.Form):
    task = forms.CharField(label="New Task")
    priority = forms.IntegerField(label="Priority", min_value=1, max_value=10)

def add(request):
    return render(request, "tasks/add.html", {
        "form": NewTaskForm()
    })
```
- Then, in the HTML itself, we can replace our HTML form code, with Django-generated HTML
```html
<form action="{% url 'tasks:add' %}" method="post">
    {% csrf_token %}
    {{ form }}
    <input type="submit">
</form>
```
- If we use a Django form, we can then reconstruct its contents from the request
- On invalid data, we are sending back the existing form, which will include errors
```python
def add(request):
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            task = form.cleaned_data["task"]
            tasks.append(task)
        else:
            return return render(request, "tasks/add.html", {
                "form": form
            })
```

## Redirecting
- Rather than redirecting to the URL directly, we should use the built-in method that will lookup from our URL patterns table
```python
from django.http import HTTPResponseRedirect
from django.urls import reverse

return HTTPResponseRedirect(reverse("tasks:index"))
```

## Data Storage and Sessions
- Bad design to store tasks inside a global variable, visible to all users
- Instead should be stored in the user's session, specific to themself
- Must run `python manage.py migrate` before using the session
```python
def index(request):
    if "tasks" not in request.session:
        request.session["tasks"] = []
```
