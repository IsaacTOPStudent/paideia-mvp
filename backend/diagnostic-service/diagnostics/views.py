from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema

from src.application.use_cases.manage_catalog import (
    CreateDiagnosticUseCase,
    ListDiagnosticUseCase, 
    CharacterizeStudentUseCase
)
from src.application.use_cases.update_diagnostic import UpdateDiagnosticUseCase
from src.application.use_cases.deactivate_diagnostic import DeactivateDiagnosticUseCase

from src.infrastructure.repositories.django_diagnostic_repository import (
    DjangoDiagnosticRepository,
    DjangoCharacterizationRepository
)
from src.domain.exceptions import (
    DiagnosticAlreadyExistsError,
    InvalidDiagnosticDataError, 
    DiagnosticInactiveError,
    DiagnosticNotFoundError,
    CharacterizationAlreadyExistsError,
    InvalidCharacterizationDataError,
    CharacterizationNotFoundError
)
from .permissions import IsAdmin, IsPsychologist, IsAdminOrPsychologist, UserRole, IsAdminPsychologistOrTeacher
from .serializers import DiagnosticSerializer, CharacterizationSerializer, DiagnosticUpdateSerializer
from typing import cast

# Create your views here.

diagnostic_repository = DjangoDiagnosticRepository()
characterization_repository = DjangoCharacterizationRepository()

@swagger_auto_schema(
    method='post',
    operation_description='Crear un nuevo diagnóstico en el catálogo (Only Admin)',
    request_body=DiagnosticSerializer,
    responses={
        201: DiagnosticSerializer,
        400: 'Datos inválidos',
        403: 'No autorizado',
        409: 'El código del diagnóstico ya existe', 
        500: 'Error inesperado en el servidor'
    }
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_diagnostic(request):
    """
    POST /api/diagnostics/catalog/
    """
    serializer = DiagnosticSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        use_case = CreateDiagnosticUseCase(diagnostic_repository)
        validated_data = cast(dict, serializer.validated_data)

        diagnostic = use_case.execute(validated_data)
        response_serializer = DiagnosticSerializer(diagnostic)

        return Response(
            {
                'message': 'Diagnóstico agregado al catálogo exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    except DiagnosticAlreadyExistsError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_409_CONFLICT
        )

    except InvalidDiagnosticDataError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='get',
    operation_description='Listar catálogo de diagnósticos NEE activos o completos',
    responses={
        200: DiagnosticSerializer(many=True),
        403: 'Token inválido o usuario inactivo.',
        500: 'Error inesperado en el servidor.'
    }
)
@api_view(['GET'])
@permission_classes([IsAdminOrPsychologist])
def list_diagnostics(request):
    """
    GET /api/diagnostics/catalog/
    """
    try:
        include_inactive = request.query_params.get('include_inactive', 'false').lower() == 'true'

        active_only = not include_inactive

        use_case = ListDiagnosticUseCase(diagnostic_repository)
        diagnostics = use_case.execute(active_only=active_only)

        serializer = DiagnosticSerializer(diagnostics, many=True)

        return Response(
            {
                'count': len(diagnostics),
                'data': serializer.data
            },
            status.HTTP_200_OK
        )
    
    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='patch',
    operation_description='Actualizar diagnóstico',
    request_body=DiagnosticUpdateSerializer,
    responses={
        200: DiagnosticSerializer,
        400: 'Datos inválidos',
        403: 'No autorizado',
        404: 'Diagnóstico no encontrado',
        409: 'Código duplicado',
        500: 'Error inesperado del servidor'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_diagnostic(request, diagnostic_id):

    serializer = DiagnosticUpdateSerializer(
        data=request.data,
        partial=True
    )

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        use_case = UpdateDiagnosticUseCase(
            diagnostic_repository
        )

        validated_data = cast(
            dict,
            serializer.validated_data
        )

        diagnostic = use_case.execute(
            diagnostic_id,
            validated_data
        )

        response_serializer = DiagnosticSerializer(
            diagnostic
        )

        return Response(
            {
                'message': 'Diagnóstico actualizado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except InvalidDiagnosticDataError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    except DiagnosticNotFoundError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )

    except DiagnosticAlreadyExistsError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_409_CONFLICT
        )

    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='patch',
    operation_description='Desactivar diagnóstico',
    responses={
        200: DiagnosticSerializer,
        403: 'No autorizado',
        404: 'No encontrado',
        500: 'Error inesperado del servidor'

    }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def deactivate_diagnostic(request, diagnostic_id):

    try:

        use_case = DeactivateDiagnosticUseCase(
            diagnostic_repository
        )

        diagnostic = use_case.execute(
            diagnostic_id
        )

        return Response(
            {
                'message': 'Diagnóstico desactivado exitosamente',
                'data': {
                    'id': diagnostic.id,
                    'is_active': diagnostic.is_active
                }
            },
            status=status.HTTP_200_OK
        )

    except DiagnosticNotFoundError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='post',
    operation_description='Caracterizar a un estudiante con un diagnóstico NEE (Solo Psicólogo - CU-04)',
    request_body=CharacterizationSerializer,
    responses={
        201: CharacterizationSerializer,
        400: 'Datos inválidos',
        403: 'No autorizado',
        404: 'Diagnóstico no encontrado o inactivo',
        500: 'Error inesperado en el servidor.'
    }
)
@api_view(['POST'])
@permission_classes([IsPsychologist])
def characterize_student(request):
    """
    POST /api/diagnostics/characterizations/
    """

    serializer = CharacterizationSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        psychologistid = request.user.id
        
        psychologist_id = int(psychologistid)

        use_case = CharacterizeStudentUseCase(diagnostic_repository, characterization_repository)

        validated_data = cast(dict, serializer.validated_data)

        characterization = use_case.execute(validated_data, psychologist_id)

        response_serializer = CharacterizationSerializer(characterization)

        return Response(
            {
                'message': 'Estudiante caracterizado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    except DiagnosticNotFoundError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
    except (DiagnosticInactiveError, InvalidDiagnosticDataError, InvalidCharacterizationDataError) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    except CharacterizationAlreadyExistsError as e:
        return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        
    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='get',
    operation_description='Obtener las caracterizaciones activas de un estudiante. Los docentes ven una versión limitada.',
    responses={
        200: 'Lista de caracterizaciones (filtrada según el rol del usuario).',
        403: 'No autorizado para consultar este estudiante.',
        404: 'Estudiante o caracterizaciones no encontradas',
        500: 'Error inesperado en el servidor.'
    }
)
@api_view(['GET'])
@permission_classes([IsAdminPsychologistOrTeacher])
def characterizations_by_student(request, student_id):
    """
    GET /api/diagnostics/student/{id}/characterizations/
    """
    token_payload = request.auth
    user_role = token_payload['role']
    try:
        characterizations = characterization_repository.find_active_by_student(student_id)

        if user_role == UserRole.TEACHER:
            return Response(
                {
                    'count': len(characterizations),
                    'data': [
                        {
                            'id': c.id,
                            'severity_level': c.severity_level.to_spanish() if hasattr(c.severity_level, 'to_spanish') else str(c.severity_level)
                        }
                        for c in characterizations
                    ]
                }, 
                status=status.HTTP_200_OK
            )
        
        serializer = CharacterizationSerializer(characterizations, many=True)

        return Response(
            {
                'count': len(characterizations),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except CharacterizationNotFoundError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception:
        return Response(
            {
                'error': 'Error interno en el servidor',
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """ 
    Health check endpoint for the diagnostic-service. Returns a simple JSON response indicating the service is running.
    """
    return Response({
        'status': 'healthy',
        'service': 'diagnostic-service',
        'version': '1.0.0',
        'database': 'connected' 
        }, status=status.HTTP_200_OK)

