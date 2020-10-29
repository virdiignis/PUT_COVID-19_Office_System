from django.utils import timezone

from django.db.models import Q
from django.views.generic import ListView

from apps.covid.models import Case


class CaseListView(ListView):
    model = Case
    paginate_by = 10

    def get_queryset(self):
        open = self.request.GET.get('open', None)
        if open == "None":
            q = Case.objects.all()
        elif open == "true":
            q = Case.objects.filter(Q(date_close__isnull=True) | Q(date_close__gt=timezone.now())).order_by('date_open')
        else:
            q = Case.objects.filter(date_close__lte=timezone.now()).order_by('date_close')

        search = self.request.GET.get('search', None)
        if search is not None:
            q = q.filter(title__icontains=search)

        return q

    def get_context_data(self, **kwargs):
        context = super(CaseListView, self).get_context_data()
        context["search"] = self.request.GET.get('search', '')
        context["open"] = self.request.GET.get('open', 'None')
        if context["open"] != 'None':
            context["open"] = context["open"] == "true"
        else:
            context["open"] = None
        return context
