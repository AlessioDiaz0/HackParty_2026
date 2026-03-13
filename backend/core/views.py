from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .classifier_logic import ZeroShotClassifier
from .models import Ticket
from datetime import datetime

from .translations_data import BASE_TRANSLATIONS

from .translator_logic import Translator

class ClassifyView(APIView):
    def post(self, request):
        prompt = request.data.get('prompt')
        if not prompt:
            return Response({"error": "Prompt field is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        classifier = ZeroShotClassifier()
        result = classifier.classify(prompt)
        
        # Save to database
        Ticket.objects.create(
            text=prompt,
            category=result['category'],
            confidence=result['confidence'],
            reasoning=result['reasoning']
        )
        
        return Response(result, status=status.HTTP_200_OK)

class TicketListView(APIView):
    def get(self, request):
        tickets = Ticket.objects.all().order_by('-created_at')
        data = []
        for t in tickets:
            data.append({
                "id": t.id,
                "text": t.text,
                "category": t.category.lower(),
                "confidence": t.confidence,
                "reasoning": t.reasoning,
                "date": t.created_at.strftime("%H:%M")
            })
        return Response(data, status=status.HTTP_200_OK)

class BaseTranslationsView(APIView):
    def get(self, request):
        return Response(BASE_TRANSLATIONS, status=status.HTTP_200_OK)

class TranslateView(APIView):
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
