from django.shortcuts import render
import markdown2

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


def entry(request, title):
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
