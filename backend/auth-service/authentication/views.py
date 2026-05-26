from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import CustomTokenObtainPairSerializer, LogoutSerializer
from .models import AuditLogModel, UserModel
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from typing import cast, Any

from src.application.use_cases.create_user import CreateUserUseCase
from src.application.use_cases.list_users import ListUsersUseCase
from src.application.use_cases.update_user import UpdateUserUseCase
from src.application.use_cases.deactivate_user import DeactivateUserUseCase
from src.application.use_cases.reactivate_user import ReactivateUserUseCase


from src.application.dtos.user_dto import CreateUserDTO, UpdateUserDTO, UserResponseDTO

from src.infrastructure.repositories.django_user_repository import DjangoUserRepository
from src.infrastructure.adapters.password_hasher import DjangoPasswordHasher

from authentication.permissions import (
    IsAdmin
)

from src.domain.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidUserDataError,
    UnauthorizedOperationError
)

from .serializers import (
    UserCreateSerializer,
    UserUpdateSerializer,
    UserResponseSerializer
)

def get_client_ip(request):
    """
        Get real IP from client
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')

user_repository = DjangoUserRepository()
password_hasher = DjangoPasswordHasher()

@swagger_auto_schema(
    method='post',
    operation_description="Crear un nuevo usuario (solo Admin)",
    request_body=UserCreateSerializer,
    responses={
        201: UserResponseSerializer,
        400: 'Datos inválidos',
        403: 'No autorizado (no eres admin)',
        409: 'Email duplicado',
        500: 'Error interno del servidor'
    }
)
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_user(request):
    """
    POST /api/auth/users/
    """

    serializer = UserCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        current_user = user_repository.find_by_id(
            request.user.id
        )

        if not current_user:
            return Response(
                {
                    'error': 'Usuario autenticado no encontrado'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        validated_data = cast(dict, serializer.validated_data)

        dto = CreateUserDTO(
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password'],
            role=validated_data['role'],
            created_by=current_user.id
        )

        use_case = CreateUserUseCase(
            user_repository,
            password_hasher
        )

        result = use_case.execute(
            dto,
            current_user
        )

        response_serializer = UserResponseSerializer(
            result.__dict__
        )

        AuditLogModel.objects.create(
            user=request.user,
            module='AUTH',
            action='CREATE_USER',
            ip_address=get_client_ip(request)
        )

        return Response(
            {
                'message': 'Usuario creado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    except UserAlreadyExistsError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_409_CONFLICT
        )

    except InvalidUserDataError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    except UnauthorizedOperationError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_403_FORBIDDEN
        )

    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Listar todos los usuarios (solo Admin)',
    manual_parameters=[
        openapi.Parameter(
            'include_inactive',
            openapi.IN_QUERY,
            description="Incluir usuarios inactivos",
            type=openapi.TYPE_BOOLEAN,
            default=False
        )
    ],
    responses={
        200: UserResponseSerializer(many=True),
        403: 'No autorizado',
        500: 'Error interno del servidor'
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def list_users(request):
    """
    GET /api/auth/users/
    """

    try:
        current_user = user_repository.find_by_id(
            request.user.id
        )

        if not current_user:
            return Response(
                {
                    'error': 'Usuario autenticado no encontrado'
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        include_inactive = (
            request.query_params
            .get('include_inactive', 'false')
            .lower() == 'true'
        )

        use_case = ListUsersUseCase(
            user_repository
        )

        result = use_case.execute(
            current_user,
            include_inactive
        )

        response_serializer = UserResponseSerializer(
            [r.__dict__ for r in result],
            many=True
        )

        AuditLogModel.objects.create(
            user=request.user,
            module='AUTH',
            action='LIST_USERS',
            ip_address=get_client_ip(request)
        )

        return Response(
            {
                'count': len(result),
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    except UnauthorizedOperationError as e:
        return Response(
            {
                'error': str(e)
            },
            status=status.HTTP_403_FORBIDDEN
        )

    except Exception:
        return Response(
            {
                'error': 'Error interno del servidor'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_description='Obtener un usuario por ID (solo Admin)',
    responses={
        200: UserResponseSerializer,
        401: 'Usuario autenticado no encontrado',
        403: 'No autorizado',
        404: 'Usuario no encontrado',
        500: 'Error inesperado en el servidor'
    }
)
@api_view(['GET'])
@permission_classes([IsAdmin])
def user_detail(request, user_id):
    """
    GET /api/auth/users/{id}/
    """

    try:
        current_user = user_repository.find_by_id(request.user.id)

        if not current_user:
            return Response(
                {'error': 'Usuario autenticado no encontrado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = user_repository.find_by_id(user_id)

        if not user:
            raise UserNotFoundError(str(user_id))

        serializer = UserResponseSerializer(
            UserResponseDTO.from_entity(user).__dict__
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    except UserNotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='patch',
    operation_description='Actualizar un usuario (solo Admin)',
    request_body=UserUpdateSerializer,
    responses={
        200: UserResponseSerializer,
        400: 'Datos inválidos',
        401: 'Usuario autenticado no encontrado',
        403: 'No autorizado',
        404: 'Usuario no encontrado',
        500: 'Error inesperado en el servidor'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def update_user(request, user_id):
    """
    PUT /api/auth/users/{id}/
    """

    serializer = UserUpdateSerializer(data=request.data, partial=True)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        current_user = user_repository.find_by_id(request.user.id)

        if not current_user:
            return Response(
                {'error': 'Usuario autenticado no encontrado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        validated_data = cast(dict, serializer.validated_data)

        dto = UpdateUserDTO(
            user_id=user_id,
            full_name=validated_data.get('full_name'),
            role=validated_data.get('role'),
            updated_by=current_user.id
        )

        use_case = UpdateUserUseCase(user_repository)

        result = use_case.execute(dto, current_user)

        AuditLogModel.objects.create(
            user=request.user,
            module='AUTH',
            action='UPDATE_USER',
            ip_address=get_client_ip(request)
        )

        response_serializer = UserResponseSerializer(
            result.__dict__
        )

        return Response(
            {
                'message': 'Usuario actualizado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    except UnauthorizedOperationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )

    except UserNotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    except InvalidUserDataError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
@swagger_auto_schema(
    method='patch',
    operation_description='Desactivar un usuario (solo Admin)',
    responses={
        200: UserResponseSerializer,
        401: 'Usuario autenticado no encontrado',
        403: 'No autorizado',
        404: 'Usuario no encontrado',
        500: 'Error inesperado en el servidor'
    }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def deactivate_user(request, user_id):
    """
    PATCH /api/auth/users/{id}/
    """

    try:
        current_user = user_repository.find_by_id(request.user.id)

        if not current_user:
            return Response(
                {'error': 'Usuario autenticado no encontrado'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        use_case = DeactivateUserUseCase(user_repository)

        result = use_case.execute(user_id, current_user)

        AuditLogModel.objects.create(
            user=request.user,
            module='AUTH',
            action='DEACTIVATE_USER',
            ip_address=get_client_ip(request)
        )

        response_serializer = UserResponseSerializer(
            result.__dict__
        )

        return Response(
            {
                'message': 'Usuario desactivado exitosamente',
                'data': response_serializer.data
            },
            status=status.HTTP_200_OK
        )

    except UnauthorizedOperationError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_403_FORBIDDEN
        )

    except UserNotFoundError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_404_NOT_FOUND
        )

    except InvalidUserDataError as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

    except Exception as e:
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
@swagger_auto_schema(
        method='patch',
        operation_description='Reactivar un usuario (solo admin)',
        responses={
            200: 'Usuario reactivado exitosamente',
            403: 'No autorizado',
            404: 'Usuario no encontrado',
            400: 'Operación inválida'
        }
)
@api_view(['PATCH'])
@permission_classes([IsAdmin])
def user_reactivate(request, user_id):
    try:
        current_user = user_repository.find_by_id(request.user.id)

        if not current_user:
            return Response({
                'error': 'Usuario autenticado no encontrado'
            }, status=status.HTTP_401_UNAUTHORIZED
            )
        
        use_case = ReactivateUserUseCase(user_repository)
        result = use_case.execute(user_id, current_user)

        AuditLogModel.objects.create(
            user=request.user,
            module='AUTH',
            action='REACTIVATE_USER',
            ip_address=get_client_ip(request)
        )

        response_serializer = UserResponseSerializer(result.__dict__)

        return Response({
            'message': 'Usuario reactivado exitosamente',
            'data': response_serializer.data
        }, status=status.HTTP_200_OK)
    
    except UnauthorizedOperationError as e:
        return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
    except UserNotFoundError as e:
        return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
    except InvalidUserDataError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': 'Error inesperado del servidor'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#Create your views here.
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
     """ 
    Health check endpoint for the auth-service. Returns a simple JSON response indicating the service is running.
     """
     return Response({
         'status': 'healthy',
         'service': 'auth-service',
         'version': '1.0.0',
         'database': 'connected' 
         }, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
        Custom view for login JWT.
        Emit access token + refresh token + user data
    """

    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)

        #Record audit only if login was successful
        if response.status_code == 200:
            try:
                data = cast(dict[str, Any], request.data)
                email = data.get('email')
                user = UserModel.objects.filter(email=email).first()
                if user:
                    AuditLogModel.objects.create(
                        user=user,
                        module='AUTH',
                        action='LOGIN',
                        ip_address=get_client_ip(request)
                    )

            except Exception:
                pass

        return response

    
@swagger_auto_schema(
    method='post',
    operation_description='Cerrar sesión e invalidar refresh token',
    request_body=LogoutSerializer,
    responses={
        200: 'Sesión cerrada',
        400: 'Token inválido'
    }
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    serializer = LogoutSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                'error': 'Datos inválidos',
                'details': serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        validated_data = cast(dict[str, Any], serializer.validated_data)
        refresh_token = validated_data['refresh']

        token = RefreshToken(refresh_token)
        token.blacklist()

        return Response(
            {
                'message': 'Sesión cerrada exitosamente'
            },
            status=status.HTTP_200_OK
        )
    
    except Exception:
        return Response(
            {
                'error': 'Refresh token inválido o expirado'
            },
            status=status.HTTP_400_BAD_REQUEST
        )


