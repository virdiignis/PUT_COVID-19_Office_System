from dal import autocomplete
from django.db.models import Q

from apps.covid.models import Person, Unit


class PersonAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Person.objects.none()

        qs = Person.objects.order_by("last_name", "first_name")

        if self.q:
            qs = qs.filter(
                Q(first_name__istartswith=self.q) |
                Q(last_name__istartswith=self.q) |
                Q(email__istartswith=self.q)
            )

        return qs


class UnitAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Unit.objects.none()

        qs = Unit.objects.order_by("name")

        if self.q:
            qs = qs.filter(
                Q(name__istartswith=self.q) |
                Q(report_students_email__istartswith=self.q) |
                Q(report_employees_email__istartswith=self.q)
            )

        return qs
