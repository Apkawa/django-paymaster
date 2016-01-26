# -*- coding: utf-8 -*-

from django.contrib import admin
from .models import Invoice, Refund


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    can_delete = False

    fields = (
        'refund_id', 'invoice', 'amount', 'refund_date'
    )
    readonly_fields = fields


    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'amount', 'payment_method',
                    'payment_id', 'payment_date', 'creation_date')
    search_fields = ['description']
    date_hierarchy = 'payment_date'

    inlines = [RefundInline]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f, _ in obj._meta.get_concrete_fields_with_model()]
        return []


admin.site.register(Invoice, InvoiceAdmin)


class RefundAdmin(admin.ModelAdmin):
    list_display = (
        'refund_id', 'invoice_id', 'amount', 'refund_date'
    )
    list_display_links = ['refund_id']
    search_fields = [
        'invoice_id', 'invoice__number', 'invoice__description'
    ]
    date_hierarchy = 'refund_date'

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return [f.name for f, _ in obj._meta.get_concrete_fields_with_model()]

        return []


admin.site.register(Refund, RefundAdmin)
