from django.db.models import Q
from rest_framework import serializers
from django_filters import FilterSet, OrderingFilter, CharFilter
from django.utils.translation import gettext_lazy as _
from .models import Vuln, ExploitMetadata, ThreatMetadata


class VulnSerializer(serializers.HyperlinkedModelSerializer):
    # cve = serializers.SerializerMethodField()
    exploit_count = serializers.SerializerMethodField()
    # rating = serializers.SerializerMethodField()
    # vulnerable_products = serializers.SerializerMethodField()

    def get_exploit_count(self, instance):
        return instance.exploit_count
        # return instance.exploitmetadata_set.count()

    class Meta:
        model = Vuln
        fields = [
            'id',
            'cveid',
            'cve_id',
            'summary', 'published', 'modified', 'assigner',
            'cvss', 'cvss_time', 'cvss_vector',
            'cwe_id', 'access', 'impact',
            'is_exploitable',
            'exploit_count',
            'score',
            'is_confirmed',
            'is_in_the_news',
            'is_in_the_wild',
            'vulnerable_products',
            'monitored',
            'reflinks',
            'reflinkids',
            'created_at', 'updated_at']


class VulnFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')
    product = CharFilter(method='filter_product', field_name='product')
    productversion = CharFilter(method='filter_productversion', field_name='productversion')
    # have_product = Filter(name="products", lookup_type='in')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(cveid__icontains=value) |
            Q(summary__icontains=value)
        )

    def filter_product(self,  queryset, name, value):
        return queryset.filter(products__in=[value])

    def filter_productversion(self,  queryset, name, value):
        return queryset.filter(productversions__in=[value])

    sorted_by = OrderingFilter(
        choices=(
            ('id', _('PHID')), ('-id', _('PHID (Desc)')),
            ('cveid', _('CVE')), ('-cveid', _('CVE (Desc)')),
            ('cvss', _('CVSS')), ('-cvss', _('CVSS (Desc)')),
            ('score', _('Score')), ('-score', _('Score (Desc)')),
            ('exploit_count', _('NB Exploits')), ('-exploit_count', _('NB Exploits (Desc)')),
            # ('exploitmetadata', _('NB Exploits')), ('-exploitmetadata', _('NB Exploits (Desc)')),
            ('monitored', _('Monitored')), ('-monitored', _('Monitored (Desc)')),
            ('published', _('Published')), ('-published', _('Published (Desc)')),
            ('updated_at', _('Updated at')), ('-updated_at', _('Updated_at (Desc)')),
            ('is_exploitable', _('Exploitable')), ('-is_exploitable', _('Not exploitable')),
            ('is_confirmed', _('Confirmed')), ('-is_confirmed', _('Not confirmed')),
        )
    )

    class Meta:
        model = Vuln
        fields = {
            'summary': ['icontains'],
            'search': ['icontains'],
            'updated_at': ['gte', 'lte'],
            # 'exploitmetadata': [],
            # 'rating': [''],
        }


class ExploitMetadataSerializer(serializers.HyperlinkedModelSerializer):
    vp = serializers.SerializerMethodField()

    def get_vp(self, instance):
        return instance.vp

    class Meta:
        model = ExploitMetadata
        fields = [
            'id',
            'publicid',
            'vuln_id',
            'vp',
            'link',
            'notes',
            'trust_level', 'tlp_level', 'source',
            'availability', 'type', 'maturity',
            # 'raw',
            'published', 'modified',
            'created_at', 'updated_at'
        ]


class ExploitMetadataFilter(FilterSet):
    search = CharFilter(method='filter_search', field_name='search')

    def filter_search(self,  queryset, name, value):
        return queryset.filter(
            Q(link__icontains=value) |
            Q(notes__icontains=value)
        )

    sorted_by = OrderingFilter(
        # tuple-mapping retains order
        choices=(
            ('trust_level', _('Trust Level')), ('-trust_level', _('Trust Level (Desc)')),
            ('tlp_level', _('TLP Level')), ('-tlp_level', _('TLP Level (Desc)')),
            ('availability', _('Availability')), ('-availability', _('Availability (Desc)')),
            ('link', _('Link')), ('-link', _('Link (Desc)')),
            ('updated_at', _('Updated at')), ('-updated_at', _('Updated_at (Desc)')),
        )
    )

    class Meta:
        model = ExploitMetadata
        fields = {
            'link': ['icontains'],
            'notes': ['icontains'],
            # 'vuln_id': ['exact'],
        }


class ThreatMetadataSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ThreatMetadata
        fields = [
            'id',
            'vuln', 'link', 'notes',
            'trust_level', 'tlp_level', 'source',
            'is_in_the_wild', 'is_in_the_news',
            'raw', 'published', 'modified',
            'created_at', 'updated_at']
