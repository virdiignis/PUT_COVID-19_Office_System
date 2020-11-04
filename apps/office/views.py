from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy


@login_required
def home(request):
    if request.user.write_access:
        return redirect(reverse_lazy('covid_dashboard'))
    else:
        return redirect(reverse_lazy('reports'))

    return render(request, "home.html")


def null(request):
    return JsonResponse({"null": None})
