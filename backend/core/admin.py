from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket
from .translator_logic import Translator

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'colored_category', 'colored_confidence', 'text_preview', 'translated_preview', 'created_at')
    list_filter = ('category', 'confidence', 'created_at')
    search_fields = ('text', 'translated_text', 'reasoning')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('text', 'translated_text', 'category', 'confidence')
        }),
        ('AI Analysis', {
            'fields': ('reasoning', 'created_at')
        }),
    )
    
    actions = ['translate_to_english', 'translate_to_italian', 'translate_to_spanish', 'translate_to_french']

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ticket = self.get_object(request, object_id)
        if ticket and not ticket.translated_text:
            # Try to infer user language from request or default to English
            target_lang = "English"
            if request.LANGUAGE_CODE == "it":
                target_lang = "Italian"
            elif request.LANGUAGE_CODE == "es":
                target_lang = "Spanish"
            elif request.LANGUAGE_CODE == "fr":
                target_lang = "French"
                
            translator = Translator()
            result = translator.translate({'text': ticket.text}, target_lang)
            ticket.translated_text = result.get('text', ticket.text)
            ticket.save()
        return super().change_view(request, object_id, form_url, extra_context)

    def _do_translation(self, request, queryset, lang_name):
        translator = Translator()
        count = 0
        for ticket in queryset:
            if ticket.text:
                result = translator.translate({'text': ticket.text}, lang_name)
                ticket.translated_text = result.get('text', ticket.text)
                ticket.save()
                count += 1
        self.message_user(request, f"Successfully translated {count} tickets to {lang_name}.")

    @admin.action(description='Translate selected tickets to English with AI')
    def translate_to_english(self, request, queryset):
        self._do_translation(request, queryset, 'English')

    @admin.action(description='Translate selected tickets to Italian with AI')
    def translate_to_italian(self, request, queryset):
        self._do_translation(request, queryset, 'Italian')

    @admin.action(description='Translate selected tickets to Spanish with AI')
    def translate_to_spanish(self, request, queryset):
        self._do_translation(request, queryset, 'Spanish')

    @admin.action(description='Translate selected tickets to French with AI')
    def translate_to_french(self, request, queryset):
        self._do_translation(request, queryset, 'French')

    @admin.display(description='Message Content')
    def text_preview(self, obj):
        return obj.text[:60] + "..." if len(obj.text) > 60 else obj.text

    @admin.display(description='Translated Content')
    def translated_preview(self, obj):
        if not obj.translated_text:
            return "-"
        return obj.translated_text[:60] + "..." if len(obj.translated_text) > 60 else obj.translated_text

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
