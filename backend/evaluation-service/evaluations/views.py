from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """ 
    Health check endpoint for the evaluation-service. Returns a simple JSON response indicating the service is running.
    """
    return Response({
        'status': 'healthy',
        'service': 'evaluation-service',
        'version': '1.0.0',
        'database': 'connected' 
        }, status=status.HTTP_200_OK)