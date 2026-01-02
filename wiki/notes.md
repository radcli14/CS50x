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
