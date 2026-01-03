from django.forms import Form, CharField, Textarea
from django.shortcuts import render, redirect
import markdown2

from . import util


class EntryForm(Form):
    """
    The Django form used for creating a new encyclopedia entry with title and content.
    """
    title = CharField(label="Title")
    content = CharField(label="Content", widget=Textarea)

    def __init__(self, title_disabled=False, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.fields['title'].disabled = title_disabled
        self.fields['title'].widget.attrs["class"] = "form-control"
        self.fields['content'].widget.attrs["class"] = "form-control"


def index(request):
    # Call search if query parameter exists
    if request.GET.get("q"):
        return search(request)  
    
    # Otherwise, render the list of all entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def create(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        title = None
        content = None
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
        else:
            return render(request, "encyclopedia/create.html", {
                "form": form
            })

        # Check if entry with this title already exists
        if util.get_entry(title) is not None:
            return render(request, "encyclopedia/create.html", {
                "error": "An entry with this title already exists.",
                "title": title,
                "content": content
            })

        # Save the new entry and redirect to its page
        util.save_entry(title, content)
        return redirect(f"/{title}")

    # If GET request, render the creation form
    form = EntryForm()
    return render(request, "encyclopedia/create.html", {
        "form": form
    })


def entry(request, title):
    # Redirect to index with query parameter if it exists
    if request.GET.get("q"):
        return redirect(f"/?q={request.GET.get('q')}")
    
    # Get the markdown for the entry and convert to HTML, or show error if not found
    md = util.get_entry(title)
    if md is None:
        content = f"<h1>{title}</h1>Entry not found!"
    else:
        content = markdown2.markdown(md)

    # Render the page
    return render(request, "encyclopedia/entry.html", {
        "title": title,
        "content": content
    })


def random(request):
    import random
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect(f"/{random_entry}")


def edit(request, title):
    """
    Edit an existing entry. GET shows the form pre-filled; POST saves changes.
    """
    if request.method == "POST":
        content = request.POST.get("content")
        # Overwrite the existing entry
        util.save_entry(title, content)
        return redirect(f"/{title}")

    # GET: render the edit form with current content
    md = util.get_entry(title)
    return render(request, "encyclopedia/edit.html", {
        "title": title,
        "content": md or ""
    })


def search(request):
    # Get the search query from the request
    query = request.GET.get("q", "")

    # First check if there is an exact match, in which case, redirect to that entry
    entries = util.list_entries()
    if query in entries:
        return redirect(f"/{query}")

    # Otherwise, find all entries that match the query, and render that list
    matches = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches
    })
