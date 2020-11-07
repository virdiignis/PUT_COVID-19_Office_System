from dal import autocomplete
from django.db.models import Q

from apps.office.models import Worker


class WorkerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Worker.objects.none()

        qs = Worker.objects.order_by("last_name", "first_name")

        if self.q:
            qs = qs.filter(
                Q(first_name__istartswith=self.q) |
                Q(last_name__istartswith=self.q) |
                Q(username__istartswith=self.q) |
                Q(email__istartswith=self.q)
            )

        return qs
