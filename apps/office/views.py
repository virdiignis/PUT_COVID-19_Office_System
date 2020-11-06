from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView

from apps.covid.models import Action
from apps.office.models import Worker


@login_required
def home(request):
    if request.user.write_access:
        return redirect(reverse_lazy('covid_dashboard'))
    else:
        return redirect(reverse_lazy('reports'))

    return render(request, "home.html")


def null(request):
    return JsonResponse({"null": None})


class WorkerDetailView(LoginRequiredMixin, DetailView):
    model = Worker

    def get_context_data(self, **kwargs):
        context = super(WorkerDetailView, self).get_context_data(**kwargs)
        context["actions"] = Action.objects.filter(made_by=context["worker"]).order_by("-datetime")[:20]
        return context
