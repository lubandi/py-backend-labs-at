from django.shortcuts import get_object_or_404, redirect, render

from .models import TodoItem


def home_page(request):
    todo_items = TodoItem.objects.all()
    return render(request, "home_page.html", {"todos": todo_items})


def create_todo(request):
    if request.method == "POST":
        title = request.POST.get("title")
        details = request.POST.get("details")
        if title:
            new_todo = TodoItem.objects.create(title=title, details=details)
            return redirect("single_todo_page", pk=new_todo.pk)
    return render(request, "create_todo.html")


def single_todo_page(request, pk):
    todo_item = get_object_or_404(TodoItem, pk=pk)

    if request.method == "POST":
        if "edit" in request.POST:
            todo_item.title = request.POST.get("title", todo_item.title)
            todo_item.details = request.POST.get("details", todo_item.details)
            todo_item.save()
        elif "complete" in request.POST:
            todo_item.completed = True
            todo_item.save()
        elif "delete" in request.POST:
            todo_item.delete()
            return redirect("home")

        return redirect("single_todo_page", pk=pk)

    return render(request, "single_todo_page.html", {"todo": todo_item})
