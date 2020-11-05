from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView

from apps.covid.automatic_actions import AutomaticLogActions
from apps.covid.forms import CaseCreateModalForm, PersonCreateModalForm, CaseUpdateForm, IsolationFormSet, \
    ActionFormSet, ActionCreateModalForm
from apps.covid.models import Case, Action, Isolation, IsolationRoom


class CaseListView(LoginRequiredMixin, ListView):
    model = Case
    paginate_by = 10
    template_name = "covid/cases.html"

    def get_queryset(self):
        open = self.request.GET.get('open', "None")
        if open == "None":
            q = Case.objects.order_by('-date_open', '-date_closed')
        elif open == "true":
            q = Case.objects.filter(Q(date_closed__isnull=True)).order_by('-date_open')
        else:
            q = Case.objects.filter(date_closed__isnull=False).order_by('-date_closed')

        search = self.request.GET.get('search', None)
        if search is not None:
            q = q.filter(
                Q(title__icontains=search) |
                Q(people__first_name__istartswith=search) |
                Q(people__last_name__istartswith=search)
            )

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
            context["isolations"].sort(key=lambda x: (x.person.health_state.severity, x.end_date))
        else:
            context["isolations"] = []

        context["actions"] = context["case"].actions.order_by("-datetime")

        return context


class CaseCreateModalView(LoginRequiredMixin, BSModalCreateView):
    model = Case
    form_class = CaseCreateModalForm
    template_name = "covid/case_new_modal.html"

    def form_valid(self, form):
        result = super(CaseCreateModalView, self).form_valid(form)
        AutomaticLogActions(self.object, self.request.user).create_case()
        return result

    def get_success_url(self):
        return reverse_lazy("case_update", args=(self.object.id,))


class CaseUpdateView(LoginRequiredMixin, UpdateView):
    model = Case
    form_class = CaseUpdateForm
    template_name = "covid/case_update.html"

    def get_context_data(self, **kwargs):
        context = super(CaseUpdateView, self).get_context_data(**kwargs)
        context["is_open"] = self.object.date_closed is None

        if self.request.POST:
            context["isolations"] = IsolationFormSet(self.request.POST, instance=self.object)
            context["actions"] = ActionFormSet(self.request.POST, instance=self.object)
        else:
            context["isolations"] = IsolationFormSet(instance=self.object)
            context["actions"] = ActionFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        isolations = context['isolations']
        actions = context['actions']

        self.object = form.save()
        valid = True

        if isolations.is_valid():
            isolations.instance = self.object
            isolations.save()
        else:
            valid = False

        if actions.is_valid():
            actions.instance = self.object
            actions.save()
        else:
            valid = False

        if valid:
            return redirect(reverse_lazy("case_details", args=(self.object.id,)))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("case_details", args=(self.object.id,))


@login_required
def case_close(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is not None:
        raise SuspiciousOperation("Case already closed.")
    case.date_closed = timezone.now().date()
    case.save()
    AutomaticLogActions(case, request.user).close_case()

    return redirect('case_details', pk=pk)


@login_required
def case_reopen(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is None:
        raise SuspiciousOperation("Case is open.")
    case.date_closed = None
    case.save()
    AutomaticLogActions(case, request.user).reopen_case()

    return redirect('case_update', pk=pk)


class PersonCreateModalView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'covid/person_new_modal.html'
    form_class = PersonCreateModalForm
    success_url = reverse_lazy('null')  # this is required, but not used

    def form_valid(self, form):
        super(PersonCreateModalView, self).form_valid(form)
        if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
            AutomaticLogActions(user=self.request.user).add_new_person(self.object)
            return JsonResponse({"id": self.object.id, "name": str(self.object)})
        else:
            return HttpResponse()


class ActionCreateModalView(LoginRequiredMixin, BSModalCreateView):
    template_name = 'covid/action_new_modal.html'
    form_class = ActionCreateModalForm
    success_url = reverse_lazy("actions")  # this is required, but not used


class ActionDetailModalView(LoginRequiredMixin, BSModalReadView):
    model = Action
    template_name = 'covid/action_detail_modal.html'


@login_required
def covid_dashboard(request):
    if not request.user.write_access:
        return redirect(reverse_lazy('home'))

    return render(request, 'covid/dashboard/dashboard.html')


class ActionDashboardView(LoginRequiredMixin, ListView):
    model = Action
    paginate_by = 5
    queryset = Action.objects.order_by("-id")
    template_name = 'covid/dashboard/actions.html'


class CaseDashboardView(LoginRequiredMixin, ListView):
    model = Case
    paginate_by = 5
    queryset = Case.objects.filter(date_closed__isnull=True).order_by("-date_open")
    allow_empty = True
    template_name = 'covid/dashboard/cases.html'


class IsolationDashboardView(LoginRequiredMixin, ListView):
    model = Isolation
    paginate_by = 5
    queryset = Isolation.objects.order_by("-id")
    allow_empty = True
    template_name = 'covid/dashboard/isolations.html'


class IsolationRoomDashboardView(LoginRequiredMixin, ListView):
    model = IsolationRoom
    paginate_by = 5
    queryset = IsolationRoom.objects.filter(resident__isnull=False).order_by("number")
    allow_empty = True
    template_name = 'covid/dashboard/isolation_rooms.html'


class ActionListView(LoginRequiredMixin, ListView):
    model = Action
    paginate_by = 10
    queryset = Action.objects.order_by("-id")
    template_name = 'covid/actions.html'


@login_required
def action_contact_content(request, pk):
    action = get_object_or_404(Action, id=pk)
    context = {
        "title": "Incoming contact content",
        "text": action.contact_content
    }
    return render(request, 'covid/text_modal.html', context)


@login_required
def action_notes(request, pk):
    action = get_object_or_404(Action, id=pk)
    context = {
        "title": "Notes",
        "text": action.notes
    }
    return render(request, 'covid/text_modal.html', context)
