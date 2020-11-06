from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import DetailView, ListView

from apps.covid.models import Action
from apps.office.forms import ReminderCreateModalForm
from apps.office.models import Worker, Reminder


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


class ReminderDashboardView(LoginRequiredMixin, ListView):
    model = Reminder
    paginate_by = 3
    queryset = Reminder.objects.filter(read_by__isnull=True).order_by("datetime")
    allow_empty = True
    template_name = 'covid/dashboard/reminders.html'


class ReminderListView(ReminderDashboardView):
    paginate_by = 10
    template_name = 'office/reminders.html'


def reminder_mark_done(request, pk):
    reminder = get_object_or_404(Reminder, id=pk)
    if reminder.read_by is None:
        reminder.read_by = request.user
        reminder.save()
        return HttpResponse()
    else:
        return HttpResponse(status=304)


class ReminderCreateModalView(LoginRequiredMixin, BSModalCreateView):
    model = Reminder
    form_class = ReminderCreateModalForm
    template_name = "office/reminder_new_modal.html"
    success_url = reverse_lazy('reminders')
