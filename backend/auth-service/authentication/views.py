from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

# Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({
        'service': 'auth-service',
        'status': 'ok'
        })