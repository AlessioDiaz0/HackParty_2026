from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .classifier_logic import ZeroShotClassifier
from .models import Ticket
from datetime import datetime
import os

from .translations_data import BASE_TRANSLATIONS

from .translator_logic import Translator

class ClassifyView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({"error": "Prompt field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Translate to English
        translated, source_lang = translate_to_english(prompt)
        
        # Classify the translated text
        classifier = ZeroShotClassifier()
        result = classifier.classify(translated)
        
        # Save to database
        Ticket.objects.create(
            text=prompt,
            translation=translated,
            source_lang=source_lang,
            target_lang="en",
            category=result['category'],
            confidence=result['confidence'],
            urgency=result.get('urgency', 'Medium'),
            reasoning=result['reasoning']
        )
        
        result['original'] = prompt
        result['translation'] = translated
        result['source_lang'] = source_lang
        result['target_lang'] = "en"
        
        return Response(result, status=status.HTTP_200_OK)

class TicketListView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        tickets = Ticket.objects.all().order_by('-created_at')
        data = []
        for t in tickets:
            data.append({
                "id": t.id,
                "text": t.text,
                "translation": t.translation,
                "source_lang": t.source_lang,
                "target_lang": t.target_lang,
                "category": t.category.lower(),
                "confidence": t.confidence,
                "urgency": t.urgency,
                "reasoning": t.reasoning,
                "date": t.created_at.strftime("%H:%M")
            })
        return Response(data, status=status.HTTP_200_OK)

class BaseTranslationsView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        return Response(BASE_TRANSLATIONS, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class TranslateView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        source_strings = request.data.get('source_strings')
        target_lang = request.data.get('target_lang')
        
        if not source_strings or not target_lang:
            return Response({"error": "Missing source_strings or target_lang"}, status=status.HTTP_400_BAD_REQUEST)
        
        translator = Translator()
        translations = translator.translate(source_strings, target_lang)
        
        return Response({
            "status": "success",
            "translations": translations
        }, status=status.HTTP_200_OK)
