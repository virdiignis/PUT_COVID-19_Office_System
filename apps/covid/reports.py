from django.db.models import Q

from apps.covid.models import HealthStateChange, Isolation, Case, Action


def prepare_report_context(start_date, end_date):
    return {
        "start_date": start_date,
        "end_date": end_date,
        "students_sick_new": HealthStateChange.objects.filter(change_to__considered_sick=True,
                                                              datetime__gte=start_date,
                                                              datetime__lte=end_date,
                                                              person__role="S").count(),
        "students_sick_dorms_new": HealthStateChange.objects.filter(change_to__considered_sick=True,
                                                                    datetime__gte=start_date,
                                                                    datetime__lte=end_date,
                                                                    person__role="S", ).exclude(person__dorm=0).count(),
        "students_quarantined_new": Isolation.objects.filter(Q(ordered_on__gte=start_date,
                                                               ordered_on__lte=end_date) |
                                                             Q(added__gte=start_date,
                                                               added__lte=end_date),
                                                             person__role="S").count(),
        "students_quarantined_dorms_new": Isolation.objects.filter(Q(ordered_on__gte=start_date,
                                                                     ordered_on__lte=end_date) |
                                                                   Q(added__gte=start_date,
                                                                     added__lte=end_date),
                                                                   person__role="S").exclude(person__dorm=0).count(),
        "employees_sick_new": HealthStateChange.objects.filter(change_to__considered_sick=True,
                                                               datetime__gte=start_date,
                                                               datetime__lte=end_date,
                                                               person__role="E").count(),
        "employees_quarantined_new": Isolation.objects.filter(Q(ordered_on__gte=start_date,
                                                                ordered_on__lte=end_date) |
                                                              Q(added__gte=start_date,
                                                                added__lte=end_date),
                                                              person__role="E").count(),
        "isolations": Isolation.objects.filter(Q(ordered_on__gte=start_date,
                                                 ordered_on__lte=end_date) |
                                               Q(added__gte=start_date,
                                                 added__lte=end_date), ).order_by("ordered_on", "added"),
        "cases_opened": Case.objects.filter(date_open__gte=start_date,
                                            date_open__lte=end_date).order_by("date_open"),
        "cases_closed": Case.objects.filter(date_closed__isnull=False,
                                            date_closed__gte=start_date,
                                            date_closed__lte=end_date).order_by("date_closed"),
        "actions": Action.objects.filter(datetime__date__range=(start_date, end_date)).order_by("datetime"),
    }
