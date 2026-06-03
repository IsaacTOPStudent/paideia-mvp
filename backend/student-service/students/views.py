from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from src.application.use_cases.register_student import RegisterStudentUseCase
from src.application.use_cases.list_students import ListStudentsUseCase
from src.application.use_cases.update_student import UpdateStudentUseCase
from src.application.use_cases.deactivate_student import DeactivateStudentUseCase

from src.infrastructure.repositories.django_student_repository import DjangoStudentRepository

from src.domain.exceptions import (
    StudentAlreadyExistsError,
    StudentNotFoundError, 
    InvalidStudentDataError
)

from .permissions import IsSecretary
from .serializers import StudentRegisterSerializer, StudentResponseSerializer, StudentUpdateSerializer
from typing import cast

student_repository = DjangoStudentRepository()

@swagger_auto_schema(
    method='post',
    operation_description='Registrar nuevo estudiante (solo Secretarias)',
    request_body=StudentRegisterSerializer,
    responses={
        201: StudentResponseSerializer,
        400: 'Datos inválidos',
        403: 'No autorizado',
        409: 'Documento duplicado',
        500: 'Error inesperado en el servidor'
    }
)
@api_view(['POST'])
@permission_classes([AllowAny])
def student_register(request):

    serializer = StudentRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        use_case = RegisterStudentUseCase(student_repository)

        validated_data = cast(dict, serializer.validated_data)

        student = use_case.execute(validated_data)

        response_serializer = StudentResponseSerializer(student)

        return Response(
            {
                'message': 'Estudiante registrado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )
    
    except StudentAlreadyExistsError as e:
        return Response({'error': str(e)}, status=status.HTTP_409_CONFLICT)
        
    except InvalidStudentDataError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Listar estudiantes registrados',
    responses={
        200: StudentResponseSerializer(many=True),
        403: "Token inválido o usuario inactivo.",
        500: "Error inesperado en el servidor"
    }
)
@api_view(['GET'])
@permission_classes([AllowAny])
def student_list(request):
    try:
        use_case = ListStudentsUseCase(student_repository)
        students = use_case.execute(include_inactive=False)

        serializer = StudentResponseSerializer(students, many=True)

        return Response(
            {
                'count': len(students),
                'data': serializer.data
            },
            status=status.HTTP_200_OK
        
        )
    
    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description="Obtiene el perfil y los detalles de un estudiante específico mediante su ID. Accesible por cualquier rol autenticado (RN-03).",
    manual_parameters=[
        openapi.Parameter(
            'student_id',
            openapi.IN_PATH,
            description="ID único del estudiante a consultar",
            type=openapi.TYPE_INTEGER, # Cambia a TYPE_STRING si usas UUIDs
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Detalles del estudiante obtenidos con éxito.",
            schema=StudentResponseSerializer
        ),
        401: "Token de autenticación faltante, expirado o inválido.",
        404: openapi.Response(
            description="El estudiante no existe en el sistema o se encuentra inactivo.",
            examples={
                "application/json": {
                    "error": "Estudiante no encontrado"
                }
            }
        ),
        500: openapi.Response(
            description="Error inesperado en el servidor.",
            examples={
                "application/json": {
                    "error": "Error interno del servidor"
                }
            }
        )
    }
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def student_detail(request, student_id):
    """
    GET /api/students/{id}/
    """

    try:
        student = student_repository.find_by_id(student_id)

        if not student or not student.is_active:
            raise StudentNotFoundError(str(student_id))
        
        serializer = StudentResponseSerializer(student)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except StudentNotFoundError:
        return Response(
            {'error': 'Estudiante no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='patch',
    operation_description='Actualizar estudiante',
    request_body=StudentUpdateSerializer,
    responses={
        200: StudentResponseSerializer,
        400: "Datos inválidos",
        404: "Estudiante no encontrado",
        500: "Error inesperado en el servidor"
    }

)
@api_view(['PATCH'])
@permission_classes([IsSecretary])
def update_student(request, student_id):

    serializer = StudentUpdateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        use_case = UpdateStudentUseCase(student_repository)

        validated_data = cast(dict, serializer.validated_data)

        student = use_case.execute(
            student_id,
            validated_data
        )

        response_serializer = StudentResponseSerializer(student)

        return Response(
            {
                'message': 'Estudiante actualizado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    except StudentNotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    except InvalidStudentDataError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='patch',
    operation_description='Desactivar estudiante'
)
@api_view(['PATCH'])
@permission_classes([IsSecretary])
def deactivate_student(request, student_id):

    try:
        use_case = DeactivateStudentUseCase(student_repository)

        student = use_case.execute(student_id)

        return Response(
            {
                'message': 'Estudiante desactivado exitosamente',
                'student_id': student.id,
                'is_active': student.is_active
            },
            status=status.HTTP_200_OK
        )

    except StudentNotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception:
        return Response(
            {'error': 'Error interno del servidor'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """ 
    Health check endpoint for the student-service. Returns a simple JSON response indicating the service is running.
    """
    return Response({
        'status': 'healthy',
        'service': 'student-service',
        'version': '1.0.0',
        'database': 'connected' 
        }, status=status.HTTP_200_OK)