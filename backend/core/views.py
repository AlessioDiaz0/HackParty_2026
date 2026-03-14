from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .classifier_logic import ZeroShotClassifier
from .models import Ticket
from datetime import datetime
import os

from .translations_data import BASE_TRANSLATIONS

from .translator_logic import Translator

# Lara Translate SDK for message translation
try:
    from lara_sdk import Translator as LaraTranslator, Credentials
    _lara_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "lara.txt")
    if os.path.exists(_lara_key_file):
        with open(_lara_key_file) as f:
            lines = f.read().strip().split("\n")
            _lara_id = lines[0].strip()
            _lara_secret = lines[1].strip()
        _lara_creds = Credentials(access_key_id=_lara_id, access_key_secret=_lara_secret)
        _lara = LaraTranslator(_lara_creds)
    else:
        _lara = None
except Exception:
    _lara = None


def translate_to_english(text):
    """Translate text to English using Lara. Returns (translated, source_lang)."""
    if not _lara:
        return text, ""
    try:
        res = _lara.translate(text, target="en-US")
        return res.translation, res.source_language
    except Exception as e:
        print(f"Lara translation error: {e}")
        return text, ""

class ClassifyView(APIView):
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
