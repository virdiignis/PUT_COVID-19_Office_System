import hashlib

from bootstrap_modal_forms.generic import BSModalCreateView, BSModalReadView, BSModalUpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import SuspiciousOperation
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Q
from django.views.generic import ListView, DetailView, UpdateView

from apps.covid.automatic_actions import AutomaticLogActions
from apps.covid.forms import CaseCreateModalForm, PersonCreateUpdateModalForm, CaseUpdateForm, IsolationFormSet, \
    ActionFormSet, ActionCreateModalForm, IsolationRoomFormSet, DocumentFormSet, ReportForm, UnitCreateModalForm
from apps.covid.models import Case, Action, Isolation, IsolationRoom, Person, HealthStateChange, Document
from apps.covid.reports import prepare_report_context
from apps.mailing.report import Report
from apps.office.safety import HasWriteAccessMixin, has_write_access


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


class CaseCreateModalView(HasWriteAccessMixin, BSModalCreateView):
    model = Case
    form_class = CaseCreateModalForm
    template_name = "covid/case_new_modal.html"

    def form_valid(self, form):
        if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
            result = super(CaseCreateModalView, self).form_valid(form)
            AutomaticLogActions(self.object, self.request.user).create_case()
            return result
        else:
            return HttpResponse()

    def get_success_url(self):
        return reverse_lazy("case_update", args=(self.object.id,))


class CaseUpdateView(HasWriteAccessMixin, UpdateView):
    model = Case
    form_class = CaseUpdateForm
    template_name = "covid/case_update.html"

    def get_context_data(self, **kwargs):
        context = super(CaseUpdateView, self).get_context_data(**kwargs)
        context["is_open"] = self.object.date_closed is None

        if self.request.POST:
            context["isolations"] = IsolationFormSet(self.request.POST, instance=self.object)
            context["actions"] = ActionFormSet(self.request.POST, instance=self.object)
            context["documents"] = DocumentFormSet(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context["isolations"] = IsolationFormSet(instance=self.object)
            if self.object.isolations.exists():
                context["isolations"].extra = 0
            context["actions"] = ActionFormSet(instance=self.object)
            context["documents"] = DocumentFormSet(instance=self.object)

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        isolations = context['isolations']
        actions = context['actions']
        documents = context['documents']

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

        if documents.is_valid():
            documents.instance = self.object
            for doc in documents:
                if doc.changed_data:
                    d = doc.save(commit=False)
                    d.file.name = f"{hashlib.sha512(d.file.read()).hexdigest()}.pdf"
                    d.uploaded_by = self.request.user
                    d.save()

        else:
            valid = False

        if valid:
            return redirect(reverse_lazy("case_details", args=(self.object.id,)))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_success_url(self):
        return reverse_lazy("case_details", args=(self.object.id,))


@login_required
@has_write_access()
def case_close(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is not None:
        raise SuspiciousOperation(_("Case already closed."))
    case.date_closed = timezone.now().date()
    case.save()
    AutomaticLogActions(case, request.user).close_case()

    return redirect('case_details', pk=pk)


@login_required
@has_write_access()
def case_reopen(request, pk: int):
    case = get_object_or_404(Case, pk=pk)
    if case.date_closed is None:
        raise SuspiciousOperation(_("Case is open."))
    case.date_closed = None
    case.save()
    AutomaticLogActions(case, request.user).reopen_case()

    return redirect('case_update', pk=pk)


class ActionCreateModalView(HasWriteAccessMixin, BSModalCreateView):
    template_name = 'covid/action_new_modal.html'
    form_class = ActionCreateModalForm
    success_url = reverse_lazy("actions")


class ActionDetailModalView(LoginRequiredMixin, BSModalReadView):
    model = Action
    template_name = 'covid/action_detail_modal.html'


@login_required
def covid_dashboard(request):
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
        "title": _("Incoming contact content"),
        "text": action.contact_content
    }
    return render(request, 'covid/text_modal.html', context)


@login_required
def action_notes(request, pk):
    action = get_object_or_404(Action, id=pk)
    context = {
        "title": _("Notes"),
        "text": action.notes
    }
    return render(request, 'covid/text_modal.html', context)


class PersonDetailView(LoginRequiredMixin, DetailView):
    model = Person

    def get_context_data(self, **kwargs):
        context = super(PersonDetailView, self).get_context_data(**kwargs)
        person = context["person"]
        context["cases"] = Case.objects.filter(people=person).order_by("-id")
        context["isolations"] = Isolation.objects.filter(person=person).order_by("-ordered_on")
        context["actions"] = Action.objects.filter(contact_from=person).order_by("-datetime")

        return context


class PersonCreateModalView(HasWriteAccessMixin, BSModalCreateView):
    template_name = 'covid/person_new_modal.html'
    form_class = PersonCreateUpdateModalForm
    success_url = reverse_lazy('null')  # this is required, but not used

    def form_valid(self, form):
        super(PersonCreateModalView, self).form_valid(form)
        if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
            AutomaticLogActions(user=self.request.user).add_new_person(self.object)
            HealthStateChange.objects.create(
                person=self.object,
                changed_by=self.request.user,
                change_to=self.object.health_state
            )
            return JsonResponse({"id": self.object.id, "name": str(self.object)})
        else:
            return HttpResponse()


class PersonUpdateModalView(HasWriteAccessMixin, BSModalUpdateView):
    model = Person
    template_name = 'covid/person_update_modal.html'
    form_class = PersonCreateUpdateModalForm

    def get_success_url(self):
        return reverse_lazy('person_details', args=(self.object.id,))

    def form_valid(self, form):
        if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
            if form.has_changed():
                new = form.save(commit=False)

                changed_data = form.changed_data
                if 'health_state' in changed_data:
                    HealthStateChange(
                        person=self.object,
                        change_from_id=form.initial["health_state"],
                        change_to=new.health_state,
                        changed_by=self.request.user
                    ).save()

                new.save()
                AutomaticLogActions(user=self.request.user).change_person(new, changed_data)

            return redirect(self.get_success_url())
        else:
            return HttpResponse()


class IsolationRoomListView(LoginRequiredMixin, ListView):
    model = IsolationRoom
    queryset = IsolationRoom.objects.order_by("number")
    template_name = 'covid/isolation_rooms.html'


@login_required
@has_write_access()
def isolation_rooms_update(request):
    if request.method == 'POST':
        formset = IsolationRoomFormSet(request.POST, request.FILES)
        if formset.is_valid():
            formset.save()
            return redirect(reverse_lazy('isolation_rooms'))
    else:
        formset = IsolationRoomFormSet()
    return render(request, 'covid/isolation_rooms_update.html', {'formset': formset})


@login_required
def reports(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            start_date = form.cleaned_data["start_date"]
            end_date = form.cleaned_data["end_date"]

            context = prepare_report_context(start_date, end_date)
            context["show_form"] = False
        else:
            context = {
                "form": form,
                "show_form": True
            }
    else:
        context = {
            "form": ReportForm(),
            "show_form": True
        }

    return render(request, 'covid/reports.html', context)


@login_required
def reports_dl(request, start_date, end_date):
    report_path = Report(start_date, end_date).get_path()
    response = HttpResponse()
    response["Content-Disposition"] = f"attachment;"
    response["X-Accel-Redirect"] = report_path
    return response


class UnitCreateModalView(HasWriteAccessMixin, BSModalCreateView):
    template_name = 'covid/unit_new_modal.html'
    form_class = UnitCreateModalForm
    success_url = reverse_lazy('null')  # this is required, but not used

    def form_valid(self, form):
        super(UnitCreateModalView, self).form_valid(form)
        if not self.request.is_ajax() or self.request.POST.get('asyncUpdate') == 'True':
            name = self.object.name
            return JsonResponse({"id": name, "name": name})
        else:
            return HttpResponse()


@login_required
def serve_document(request, id):
    document = get_object_or_404(Document, id=id)
    name = document.name
    if not name.endswith(".pdf"):
        name += ".pdf"
    response = HttpResponse()
    response["Content-Disposition"] = f"attachment; filename={name}"
    response["X-Accel-Redirect"] = "/media" + document.file.path.split("/media")[1]
    return response
