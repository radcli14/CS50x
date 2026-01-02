from django.shortcuts import render, redirect
import markdown2

from . import util


def index(request):
    # Call search if query parameter exists
    if request.GET.get("q"):
        return search(request)  
    
    # Otherwise, render the list of all entries
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
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


def search(request):
    # Get the search query from the request
    query = request.GET.get("q", "")

    # First check if there is an exact match, in which case, redirect to that entry
    entries = util.list_entries()
    if query in entries:
        return entry(request, query)

    # Otherwise, find all entries that match the query, and render that list
    matches = [entry for entry in entries if query.lower() in entry.lower()]
    return render(request, "encyclopedia/search.html", {
        "query": query,
        "matches": matches
    })
