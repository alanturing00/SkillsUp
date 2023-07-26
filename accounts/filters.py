import django_filters
from taggit.models import TaggedItem
from .models import Profile
from taggit.managers import TaggableManager
from django.db.models import Count

class ProfileFilter(django_filters.FilterSet):
    tags = django_filters.CharFilter(method='filter_tags')

    class Meta:
        model = Profile
        fields = ['tags']

    def filter_tags(self, queryset, name, value):
        return queryset.filter(tags__name__in=[value])

    @property
    def qs(self):
        parent = super().qs
        return parent.annotate(tags_count=Count('tags'))

    def get_top_tags(self):
        return self.qs.values('tags__name').annotate(count=Count('tags__name')).order_by('-count')[:10]

    Meta.filter_overrides = {
        TaggableManager: {
            'filter_class': django_filters.CharFilter,
            'extra': lambda f: {
                'method': 'filter_tags',},},
}