from django.http import Http404
from django.shortcuts import render, redirect
from MainApp.models import Snippet, Comment
from MainApp.forms import SnippetForm, UserRegistrationForm, CommentForm
from django.contrib import auth
from django.db.models import Q


def index_page(request):
    context = {'pagename': 'PythonBin'}
    return render(request, 'pages/index.html', context)


def add_snippet_page(request):
    if request.method == "GET":
        form = SnippetForm()
        context = {
            'pagename': 'Добавление нового сниппета',
            'form': form,
        }
        return render(request, 'pages/add_snippet.html', context)
    elif request.method == "POST":
        form = SnippetForm(request.POST)
        if form.is_valid():
            snippet = form.save(commit=False)
            snippet.user = request.user
            snippet.save()
            return redirect("snippets-list")


def snippets_page(request):

    context = {
        'pagename': 'Просмотр сниппетов',
    }
    if not request.user.is_authenticated:
        snippets = Snippet.objects.filter(private=False)
    else:
        snippets = Snippet.objects.filter(Q(private=False)| Q(user=request.user))
    if request.GET.get("lang"):
        snippets = snippets.filter(lang=request.GET['lang'])
        context['lang'] = request.GET['lang']
    if request.GET.get('sort'):
        snippets = snippets.order_by(request.GET.get('sort'))
    context['snippets'] = snippets
    return render(request, 'pages/view_snippets.html', context)


def snippet_detail(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    comment_form = CommentForm()
    context = {
        'pagename': 'Информация о сниппете',
        'snippet': snippet,
        'comment_form': comment_form,
    }
    return render(request, 'snippet_detail.html', context)


def login(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
        else:
            context = {
                'errors': 'Логин или пароль некорректны',
            }
            return render(request, 'pages/index.html', context)
    return redirect(request.META.get('HTTP_REFERER', '/'))


def logout(request):
    auth.logout(request)
    return redirect('home')


def registration(request):
    if request.method == "GET":
        form = UserRegistrationForm()
        context = {
            'form': form,
        }
        return render(request, 'pages/registration.html', context)
    elif request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            context = {
                'form': form,
            }
            return render(request, 'pages/registration.html', context)


def snippets_my(request):
    my_snippet = Snippet.objects.filter(user=request.user)
    context = {
        'pagename': 'Мои сниппеты',
        'snippets': my_snippet,
    }
    return render(request, 'pages/view_snippets.html', context)


def snippet_delete(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)
    snippet.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


def snippet_edit(request, snippet_id):
    snippet = Snippet.objects.get(pk=snippet_id)

    context = {
        'snippet': snippet,
        'pagename': 'редактирование',
    }
    return render(request, 'snippet_edit_detail.html', context)


def comment_add(request):
   if request.method == "POST":
       comment_form = CommentForm(request.POST)
       if comment_form.is_valid():
           snippet_id = request.POST.get("snippet_id")
           comment = comment_form.save(commit=False)
           comment.author = request.user
           comment.snippet = Snippet.objects.get(pk=snippet_id)
           comment.save()
           return redirect(request.META.get('HTTP_REFERER', '/'))
