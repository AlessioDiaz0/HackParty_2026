from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'colored_category', 'colored_confidence', 'text_preview', 'created_at')
    list_filter = ('category', 'confidence', 'created_at')
    search_fields = ('text', 'reasoning')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('text', 'category', 'confidence')
        }),
        ('AI Analysis', {
            'fields': ('reasoning', 'created_at')
        }),
    )

    @admin.display(description='Message Content')
    def text_preview(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

    @admin.display(description='Category')
    def colored_category(self, obj):
        colors = {
            'bug': '#ef4444',
            'task': '#3b82f6',
            'enhancement': '#10b981',
            'research': '#8b5cf6',
            'design': '#ec4899',
            'testing': '#f59e0b',
            'deployment': '#06b6d4',
            'documentation': '#64748b'
        }
        color = colors.get(obj.category.lower(), '#64748b')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold; text-transform: uppercase; font-size: 10px;">{}</span>',
            color, obj.category
        )

    @admin.display(description='Confidence')
    def colored_confidence(self, obj):
        colors = {'high': '#10b981', 'medium': '#f59e0b', 'low': '#ef4444'}
        color = colors.get(obj.confidence.lower(), '#64748b')
        return format_html(
            '<span style="color: {}; font-weight: bold;">● {}</span>',
            color, obj.confidence.upper()
        )

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-created_at')
