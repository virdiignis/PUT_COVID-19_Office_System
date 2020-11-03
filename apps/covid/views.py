from bootstrap_modal_forms.generic import BSModalCreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone

from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView

from apps.covid.forms import CaseCreateModalForm, PersonCreateModalForm, CaseUpdateForm
from apps.covid.models import Case, Person


class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    paginate_by = 10

    def get_queryset(self):
        open = self.request.GET.get('open', "None")
        if open == "None":
            q = Case.objects.order_by('date_open', 'date_closed')
        elif open == "true":
            q = Case.objects.filter(Q(date_closed__isnull=True)).order_by('date_open')
        else:
            q = Case.objects.filter(date_closed__isnull=False).order_by('date_closed')

        search = self.request.GET.get('search', None)
        if search is not None:
            q = q.filter(title__icontains=search)

        return q

    def get_context_data(self, **kwargs):
        context = super(CaseListView, self).get_context_data(**kwargs)
        context["search"] = self.request.GET.get('search', '')
        context["open"] = self.request.GET.get('open', 'None')
        if context["open"] != 'None':
            context["open"] = context["open"] == "true"
        else:
            context["open"] = None
        return context


class CaseDetailView(LoginRequiredMixin, DetailView):
    model = Case

    def get_context_data(self, **kwargs):
        context = super(CaseDetailView, self).get_context_data(**kwargs)
        context["closed"] = context["case"].date_closed is not None
        if context["case"].isolations.exists():
            context["isolations"] = list(context["case"].isolations.all())
            context["isolations"].sort(key=lambda x: x.person.health_state.severity)
        else:
            context["isolations"] = []

        context["actions"] = context["case"].actions.order_by("-datetime")

        return context


class CaseCreateModalView(LoginRequiredMixin, BSModalCreateView):
    model = Case
    form_class = CaseCreateModalForm
    template_name = "covid/case_new_modal.html"

    def get_success_url(self):
        return reverse_lazy("case_update", args=(self.object.id,))


class PersonCreateModalView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'covid/person_new_modal.html'
    form_class = PersonCreateModalForm

    def get_success_url(self):
        if self.object.id is not None:
            return reverse_lazy('person_detail_json', args=(self.object.id,))
        else:
            return reverse_lazy('null')

    # def form_valid(self, form):
    #     super(PersonCreateModalView, self).form_valid(form)
    #     return JsonResponse({"id": self.object.id})


@login_required
def person_detail_json(request, pk):
    person = get_object_or_404(Person, pk=pk)
    data = {
        "id": person.id,
        "name": str(person)
    }
    return JsonResponse(data)


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseUpdateForm
    template_name = "covid/case_update.html"

    def get_context_data(self, **kwargs):
        context = super(CaseUpdateView, self).get_context_data(**kwargs)
        context["is_open"] = self.object.date_closed is None
        return context

    def get_success_url(self):
        return reverse_lazy("case_details", args=(self.object.id,))


@login_required
def case_close(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is not None:
        raise SuspiciousOperation("Case already closed.")
    case.date_closed = timezone.now().date()
    case.save()

    return redirect('case_details', pk=pk)


@login_required
def case_reopen(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is None:
        raise SuspiciousOperation("Case is open.")
    case.date_closed = None
    case.save()

    return redirect('case_update', pk=pk)
