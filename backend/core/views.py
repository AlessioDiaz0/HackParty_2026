from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .classifier_logic import ZeroShotClassifier
from .models import Ticket
from datetime import datetime

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
                "date": t.created_at.strftime("%H:%M")
            })
        return Response(data, status=status.HTTP_200_OK)
