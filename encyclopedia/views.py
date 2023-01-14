from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from markdown2 import Markdown
from random import randint
from . import util

class NewForm(forms.Form):
    title = forms.CharField(
        required=True ,
        error_messages={'required': 'Please enter your title'},
        widget=forms.TextInput(
            attrs={"placeholder": "Title", "class": "form-control col-6"}
        ))

    content = forms.CharField(
    required=True ,
    error_messages={'required': 'Please enter your content'},
    widget=forms.Textarea(
        attrs={"placeholder": "content", "class": "form-control col-6"} 
        ))
    


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })



def wiki(request,title):
    content = util.get_entry(title)
    if  content is None:
        return render(request, "encyclopedia/error.html",{'message':"requested page not found!"})

    return render(request, "encyclopedia/view.html", {
        "content": Markdown().convert(content),
        "title": title
    })


def search(request):
    list_title = []
    list_entries =  util.list_entries()
    title = request.GET.get('q')
    if not title:
        return HttpResponseRedirect(reverse("index"))
    
    for entry in list_entries:
        if title.lower() == entry.lower():
             return HttpResponseRedirect(reverse("wiki",kwargs={'title': title}))
            
    for entry in list_entries:
        if title.lower() in entry.lower():
            list_title.append(entry)
            
    if len(list_title) > 0:
        return render(request, "encyclopedia/search.html", {
            "titles": list_title
        })
    else:
        return render(request, "encyclopedia/error.html",{'message':"no results found!"})



def create(request):
    if request.method == "POST":
        form = NewForm(request.POST)
        
        if form.is_valid():
            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            list_entries =  util.list_entries()
            for entry in list_entries:
                if  title.lower() == entry.lower():
                    return render(request, "encyclopedia/create.html",{
                        'message':f' title "{title}" already exists',
                        "form": form
                        })

            util.save_entry(title,content)
            return HttpResponseRedirect(reverse("wiki",kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/create.html", {
                 "form": form
            })
    else:
        return render(request, "encyclopedia/create.html", {
            "form": NewForm()
        })


def edit(request,title):
    if request.method == "POST":
        form = NewForm(request.POST)
       
        if form.is_valid():
            content = form.cleaned_data["content"]
            util.save_entry(title,content)
            return HttpResponseRedirect(reverse("wiki",kwargs={'title': title}))
        else:
            return render(request, "encyclopedia/edit.html", {
                 "form": form
            })
    else:
        content = util.get_entry(title)
        return render(request, "encyclopedia/edit.html", {
            "form": NewForm({"title": title, "content": content}),
            'title': title
        })


def random(request):
    list_entries =  util.list_entries()
    random_index = randint(0, len(list_entries)-1)
    random_title  = list_entries[random_index]
    return HttpResponseRedirect(reverse("wiki",kwargs={'title': random_title}))



