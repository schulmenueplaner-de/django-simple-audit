# -*- coding:utf-8 -*_
from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.utils.translation import ugettext_lazy as _
from django.utils.html import escape
from django.core.urlresolvers import reverse
from .models import Audit
from .signal import CONTENTTYPE_LIST


class ContentTypeListFilter(SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('content type')
    parameter_name = 'content_type__id__exact'

    def lookups(self, request, model_admin):
            """
            Returns a list of tuples. The first element in each
            tuple is the coded value for the option that will
            appear in the URL query. The second element is the
            human-readable name for the option that will appear
            in the right sidebar.
            """
            return [(ct.pk, ct.name) for ct in CONTENTTYPE_LIST]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(content_type_id=self.value())
        else:
            return queryset


class AuditAdmin(admin.ModelAdmin):
    search_fields = ("audit_request__user__username", "description", "audit_request__request_id", )
    list_display = ("audit_date", "audit_content", "operation", "audit_user", "audit_description", )
    list_filter = ("operation", ContentTypeListFilter,)

    def audit_description(self, audit):
        desc = "<br/>".join(escape(audit.description or "").split('\n'))
        return desc
    audit_description.allow_tags = True
    audit_description.short_description = "Description"

    def audit_content(self, audit):
        if audit.content_object:
            obj_string = audit.content_object
        else:
            obj_string = u""

        return "<a title='Click to filter' href='%(base)s?content_type__id__exact=%(type_id)s&object_id__exact=%(id)s'>%(type)s: %(obj)s</a>" % {
            'base': reverse('admin:simple_audit_audit_changelist'),
            'type': audit.content_type,
            'type_id': audit.content_type.id,
            'obj': obj_string,
            'id': audit.object_id}
    audit_content.short_description = "Current Content"
    audit_content.allow_tags = True

    def audit_date(self, audit):
        return audit.audit_request.date
    audit_date.admin_order_field = "audit_request__date"
    audit_date.short_description = u"Date"

    def audit_user(self, audit):
        return u"<a title='Click to filter' href='%s?user=%d'>%s</a>" \
            % (reverse('admin:simple_audit_audit_changelist'), audit.audit_request.user.id, audit.audit_request.user)
    audit_user.admin_order_field = "audit_request__user"
    audit_user.short_description = u"User"
    audit_user.allow_tags = True

    def queryset(self, request):
        request.GET = request.GET.copy()
        user_filter = request.GET.pop("user", None)
        qs = Audit.objects.prefetch_related("audit_request", "audit_request__user")
        if user_filter:
            qs = qs.filter(audit_request__user__in=user_filter)
        return qs

    def has_add_permission(self, request):
            return False

admin.site.register(Audit, AuditAdmin)