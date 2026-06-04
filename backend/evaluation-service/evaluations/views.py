"""
Views del evaluation-service.

CU-05: Registrar Evaluación Psicológica   → evaluation_register
CU-06: Registrar Observación Académica    → observation_register
CU-07: Historial Longitudinal             → longitudinal_history

Permisos aplicados:
- RN-01: Control de acceso por rol
- RN-09: Solo Psicólogo escribe evaluaciones
- RN-10: Docente obtiene vista restringida
"""
import logging
from typing import cast

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

from evaluations.serializers import (
    PsychologicalEvaluationRegisterSerializer,
    PsychologicalEvaluationResponseSerializer,
    AcademicObservationRegisterSerializer,
    AcademicObservationResponseSerializer,
)
from evaluations.permissions import (
    IsPsychologist,
    IsAdminOrPsychologist,
    IsTeacher,
    IsAdminPsychologistOrTeacher,
)
from src.domain.exceptions import (
    EvaluationNotFoundError,
    ObservationAccessDeniedError,
    ObservationNotFoundError,
    InvalidEvaluationDataError,
    InvalidObservationDataError,
    StudentNotFoundError,
    StudentNotCharacterizedError,
    ExternalServiceError,
)
from config.dependencies import (
    register_evaluation_use_case,
    register_observation_use_case,
    get_longitudinal_history_use_case,
    evaluation_repository,
    observation_repository,
    list_evaluations_use_case,
    list_observations_use_case
)

from src.application.use_cases.evaluation_detail import GetEvaluationUseCase
from src.application.use_cases.observation_detail import GetObservationUseCase

logger = logging.getLogger(__name__)

# HELPER

def _get_token_data(request) -> tuple[int, str]:
    """
    Extraer user_id y role del JWT.
    Ambos campos son inyectados por auth-service al emitir el token.
    """
    payload = request.auth
    user_id = payload.get("user_id")
    role = payload.get("role", "")
    return user_id, role


def _service_error_response(error: ExternalServiceError) -> Response:
    """
    Respuesta estándar para errores de integración entre servicios.
    503 indica que el fallo es externo, no de esta petición.
    """
    logger.error(f"[EXTERNAL SERVICE ERROR] {error}")
    return Response(
        {"error": str(error)},
        status=status.HTTP_503_SERVICE_UNAVAILABLE,
    )

# CU-05: EVALUACIONES PSICOLÓGICAS

@swagger_auto_schema(
    method="post",
    operation_summary="Registrar evaluación psicológica periódica",
    operation_description=(
        "Registra una nueva evaluación psicológica para un estudiante con NEE. "
    ),
    request_body=PsychologicalEvaluationRegisterSerializer,
    responses={
        201: openapi.Response(
            description="Evaluación registrada con éxito",
            schema=PsychologicalEvaluationResponseSerializer,
        ),
        400: openapi.Response(
            description="Datos inválidos",
            examples={
                "application/json": {
                    "error": "Datos de evaluación inválidos",
                    "details": {"description": ["Este campo es obligatorio."]},
                }
            },
        ),
        401: openapi.Response(description="No autenticado (Falta Token JWT)"),
        403: openapi.Response(
            description="No autorizado. El actor debe ser Psicólogo"
        ),
        404: openapi.Response(
            description="Estudiante no encontrado en el sistema",
            examples={
                "application/json": {"error": "Estudiante con ID 123 no encontrado"}
            },
        ),
        422: openapi.Response(
            description="Entidad no procesable. El estudiante no posee caracterización NEE",
            examples={
                "application/json": {
                    "error": "El estudiante no cuenta con un diagnóstico de Necesidades Educativas Especiales activo."
                }
            },
        ),
        503: openapi.Response(
            description="Servicio externo no disponible)",
            examples={
                "application/json": {
                    "error": "El servicio de diagnósticos no responde. Intente más tarde."
                }
            },
        ),
    },
)
@api_view(["POST"])
@permission_classes([IsPsychologist])
def evaluation_register(request):
    """
    POST /api/evaluations/register/

    CU-05: Registrar evaluación psicológica periódica.
    Actor: Psicólogo (RN-09)

    Flujo:
    1. Valida el serializer (RN-20)
    2. Verifica que el estudiante existe en student-service
    3. Verifica que tiene NEE en diagnostic-service (RN-03)
    4. Crea la evaluación y actualiza seguimiento (RN-11)

    Errores:
    - 400: Datos inválidos (RN-20)
    - 404: Estudiante no encontrado
    - 422: Sin caracterización NEE (RN-03)
    - 503: Servicio externo no disponible
    """
    psychologist_id, requester_role = _get_token_data(request)

    # RN-20: Validar datos de entrada
    serializer = PsychologicalEvaluationRegisterSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {
                "error": "Datos de evaluación inválidos",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        evaluation = register_evaluation_use_case.execute(
            data=cast(dict, serializer.validated_data),
            psychologist_id=psychologist_id,
            requester_role=requester_role,
        )

        logger.info(
            f"[EVALUATION REGISTERED] "
            f"student_id={evaluation.student_id} "
            f"psychologist_id={psychologist_id} "
            f"next_date={evaluation.next_evaluation_date}"
        )

        response_serializer = PsychologicalEvaluationResponseSerializer(evaluation)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    except StudentNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except StudentNotCharacterizedError as e:
        # 422: La petición es válida pero no se puede procesar
        # sin la precondición de NEE (RN-03)
        return Response(
            {"error": str(e)},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except InvalidEvaluationDataError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    
    except ExternalServiceError as e:
        return _service_error_response(e)
    
    except Exception as e:
        logger.exception("[UNEXPECTED ERROR] error inesperado del servidor")

        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method="get",
    operation_summary="Listar evaluaciones activas de un estudiante",
    operation_description=(
        "Obtiene todas las evaluaciones psicológicas asociadas de forma activa "
        "a un estudiante mediante su ID proporcionado en los query parameters. "
    ),
    manual_parameters=[
        openapi.Parameter(
            name="student_id",
            in_=openapi.IN_QUERY,
            description="ID único del estudiante a consultar",
            type=openapi.TYPE_INTEGER,
            required=True,
        )
    ],
    responses={
        200: openapi.Response(
            description="Lista de evaluaciones obtenida con éxito",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "student_id": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="ID del estudiante consultado",
                    ),
                    "count": openapi.Schema(
                        type=openapi.TYPE_INTEGER,
                        description="Cantidad total de evaluaciones en los resultados",
                    ),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Schema(
                            type=openapi.TYPE_OBJECT
                        , ref="#/definitions/PsychologicalEvaluationResponse"), # Autoreferenciado por DRF-YASG si pasas el serializer
                    ),
                },
            ),
        ),
        400: openapi.Response(
            description="Falta el parámetro student_id o no es un número válido",
            examples={
                "application/json": {
                    "error": "'student_id' debe ser un número válido"
                }
            },
        ),
        401: openapi.Response(description="No autenticado"),
        403: openapi.Response(
            description="No autorizado. Solo Psicólogos o Administradores pueden consultar."
        ),
        404: openapi.Response(
            description="El estudiante no existe en el sistema",
            examples={
                "application/json": {"error": "Estudiante no encontrado."}
            },
        ),
        503: openapi.Response(
            description="Error en la comunicación con servicios externos"
        ),
    },
)
@api_view(["GET"])
@permission_classes([IsAdminOrPsychologist])
def evaluation_list(request):
    """
    GET /api/evaluations/?student_id=<id>

    Listar evaluaciones activas de un estudiante.
    Actor: Psicólogo, Administrador

    Query params:
    - student_id (requerido): ID del estudiante a consultar
    """
    student_id_param = request.query_params.get("student_id")

    if not student_id_param:
        return Response(
            {"error": "El parámetro 'student_id' es requerido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        student_id = int(student_id_param)

    except ValueError:
        return Response(
            {"error": "'student_id' debe ser un número válido"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        use_case = list_evaluations_use_case
        evaluations = use_case.execute(student_id)

        logger.info(
            f"[EVALUATIONS LIST] "
            f"student_id={student_id} " 
            f"count={len(evaluations)}"
        )

        serializer = PsychologicalEvaluationResponseSerializer(evaluations, many=True)

        return Response(
            {
                "student_id": student_id,
                "count": len(evaluations),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )

    except StudentNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except ExternalServiceError as e:
        return _service_error_response(e)
    
    except Exception:
        logger.exception("[UNEXPECTED ERROR] evaluation_list")

        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_summary="Obtener detalle de una evaluación psicológica",
    operation_description=(
        "Permite consultar el detalle completo de una evaluación psicológica "
        "específica utilizando su ID. "
    ),
    responses={
        200: openapi.Response(
            description="Evaluación encontrada con éxito.",
            schema=PsychologicalEvaluationResponseSerializer
        ),
        401: openapi.Response(
            description="No autenticado. Token JWT ausente o inválido."
        ),
        403: openapi.Response(
            description="No autorizado. El actor actual no tiene permisos de Psicólogo o Administrador."
        ),
        404: openapi.Response(
            description="Evaluación no encontrada en el repositorio.",
            examples={
                "application/json": {"error": "Evaluación con id 123 no encontrada."}
            }
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={
                "application/json": {"error": "Error interno del servidor"}
            }
        )
    }
)
@api_view(["GET"])
@permission_classes([IsAdminOrPsychologist])
def evaluation_detail(request, evaluation_id: int):
    """
    GET /api/evaluations/<evaluation_id>/

    Detalle de una evaluación específica.
    Actor: Psicólogo, Administrador
    """
    try:
        use_case = GetEvaluationUseCase(evaluation_repository)

        evaluation = use_case.execute(evaluation_id)

        logger.info(
            f"[EVALUATION DETAIL] "
            f"evaluation_id={evaluation_id}"
        )

        serializer = PsychologicalEvaluationResponseSerializer(evaluation)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except EvaluationNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND
        )
    
    except Exception:
        logger.exception("[UNEXPECTED ERROR] evaluation_detail")

        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# CU-06: OBSERVACIONES ACADÉMICAS

@swagger_auto_schema(
    method='post',
    operation_summary="Registrar observación académica",
    operation_description=(
        "Permite al Docente registrar una observación académica/pedagógica "
        "este endpoint solo procesa datos pedagógicos y no expone datos clínicos. "
        "Si el estudiante no registra Necesidades Educativas Especiales (NEE), "
        "la regla permite continuar el registro retornando una advertencia (warning)."
    ),
    request_body=AcademicObservationRegisterSerializer,
    responses={
        201: openapi.Response(
            description=(
                "Observación registrada exitosamente. Puede incluir una propiedad "
                "'warning' si el estudiante no posee un diagnóstico de NEE activo."
            ),
            schema=AcademicObservationResponseSerializer,
            examples={
                "application/json_con_advertencia": {
                    "id": 45,
                    "student_id": 12,
                    "subject": "MATEMATICAS",
                    "description": "El estudiante presenta excelente rendimiento pero requiere apoyos visuales.",
                    "created_at": "2026-06-02T11:00:00Z",
                    "warning": "El estudiante no cuenta con un diagnóstico de NEE registrado."
                }
            }
        ),
        400: openapi.Response(
            description="Datos de observación inválidos o mal formateados.",
            examples={
                "application/json_campos_faltantes": {
                    "error": "Datos de observación inválidos",
                    "details": {"subject": ["Este campo es obligatorio."]}
                },
                "application/json_logica_invalida": {
                    "error": "La descripción pedagógica no cumple con la longitud mínima."
                }
            }
        ),
        401: openapi.Response(
            description="No autenticado. Token JWT ausente o inválido."
        ),
        403: openapi.Response(
            description="No autorizado. Solo los usuarios con rol Docente pueden ejecutar esta acción."
        ),
        404: openapi.Response(
            description="El estudiante especificado no existe en el microservicio de estudiantes.",
            examples={
                "application/json": {"error": "Estudiante con id 12 no encontrado"}
            }
        ),
        502: openapi.Response(
            description="Fallo de comunicación con servicios externos (student-service o gateway).",
            examples={
                "application/json": {"error": "El servicio de estudiantes no responde. Intente más tarde."}
            }
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={
                "application/json": {"error": "Error interno del servidor"}
            }
        )
    }
)
@api_view(["POST"])
@permission_classes([IsTeacher])
def observation_register(request):
    """
    POST /api/observations/register/

    CU-06: Registrar observación académica en el aula.
    Actor: Docente (RN-09)

    RN-10: Solo recibe datos pedagógicos.
            No expone ni procesa datos clínicos.

    Flujo:
    1. Valida el serializer (RN-20)
    2. Verifica que el estudiante existe en student-service
    3. Registra la observación vinculada al historial

    Notas:
    - EX-02: Si el estudiante no tiene NEE, se permite
             el registro con advertencia (no bloquea)
    """
    teacher_id, requester_role = _get_token_data(request)

    # RN-20: Validar datos de entrada
    serializer = AcademicObservationRegisterSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            {
                "error": "Datos de observación inválidos",
                "details": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        observation, warning = register_observation_use_case.execute(
            data=cast(dict, serializer.validated_data),
            teacher_id=teacher_id,
            requester_role=requester_role,
        )

        logger.info(
            f"[OBSERVATION REGISTERED] "
            f"student_id={observation.student_id} "
            f"teacher_id={teacher_id} "
            f"subject={observation.subject.value}"
        )

        response_serializer = AcademicObservationResponseSerializer(observation)

        response_data = dict(response_serializer.data)

        if warning: 
            response_data["warning"] = warning

        return Response(response_data, status=status.HTTP_201_CREATED)

    except StudentNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    except InvalidObservationDataError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except ExternalServiceError as e:
        return _service_error_response(e)
    
    except Exception:
        logger.exception(
            "[UNEXPECTED ERROR] observation_register"
        )
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@swagger_auto_schema(
    method='get',
    operation_summary="Listar observaciones académicas de un estudiante",
    operation_description=(
        "Permite obtener el listado de observaciones pedagógicas asociadas a un estudiante. "
        "Aplica un filtro automático para retornar únicamente las observaciones "
        "que hayan sido creadas por el docente solicitante."
    ),
    manual_parameters=[
        openapi.Parameter(
            name='student_id',
            in_=openapi.IN_QUERY,
            description="ID único del estudiante del cual se desean listar las observaciones.",
            type=openapi.TYPE_INTEGER,
            required=True
        )
    ],
    responses={
        200: openapi.Response(
            description="Listado de observaciones obtenido con éxito.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "student_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID del estudiante consultado."),
                    "count": openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad total de elementos retornados."),
                    "results": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                        description="Colección de observaciones académicas filtradas."
                    )
                }
            )
        ),
        400: openapi.Response(
            description="Error en los parámetros de la solicitud.",
            examples={
                "application/json_falta_parametro": {"error": "El parámetro 'student_id' es requerido"},
                "application/json_tipo_invalido": {"error": "'student_id' debe ser un número entero válido"}
            }
        ),
        401: openapi.Response(description="No autenticado. Token JWT ausente o inválido."),
        403: openapi.Response(description="No autorizado. El rol actual no tiene acceso a esta funcionalidad."),
        404: openapi.Response(
            description="El estudiante no fue encontrado en el microservicio correspondiente.",
            examples={"application/json": {"error": "Estudiante con id 12 no encontrado."}}
        ),
        502: openapi.Response(
            description="Error de comunicación con el servicio externo de estudiantes.",
            examples={"application/json": {"error": "Servicio de estudiantes no disponible de manera temporal."}}
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={"application/json": {"error": "Error interno del servidor"}}
        )
    }
)
@api_view(["GET"])
@permission_classes([IsAdminPsychologistOrTeacher])
def observation_list(request):
    """
    GET /api/observations/?student_id=<id>

    Listar observaciones de un estudiante.

    Vista según rol (RN-10):
    - Psicólogo / Admin: todas las observaciones del estudiante
    - Docente (FA-01 del CU-06): solo sus propias observaciones

    Query params:
    - student_id (requerido): ID del estudiante
    """
    student_id_param = request.query_params.get("student_id")

    if not student_id_param:
        return Response(
            {"error": "El parámetro 'student_id' es requerido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        student_id = int(student_id_param)

        requester_id, requester_role = _get_token_data(request)

        observations = (
            list_observations_use_case.execute(
                student_id=student_id,
                requester_id=requester_id,
                requester_role=requester_role
            )
        )

        serializer = (
            AcademicObservationResponseSerializer(
                observations, 
                many=True
            )
        )

        return Response(
            {
                "student_id": student_id,
                "count": len(observations),
                "results": serializer.data
            },
            status=status.HTTP_200_OK
        )
    
    except ValueError:
        return Response(
            {"error": "'student_id' debe ser un número entero válido"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    except StudentNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    except ExternalServiceError as e:
        return _service_error_response(e)
    
    except Exception:
        logger.exception(
            "[UNEXPECTED ERROR] observation_list"
        )
        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@swagger_auto_schema(
    method='get',
    operation_summary="Obtener el detalle de una observación específica",
    operation_description=(
        "Permite recuperar la información detallada de una observación académica mediante su ID. "
        "- Los Psicólogos y Administradores pueden visualizar cualquier observación.\n"
        "- Los Docentes solo pueden consultar el detalle si ellos son los autores de dicha observación. "
    ),
    responses={
        200: openapi.Response(
            description="Detalle de la observación recuperado exitosamente.",
            schema=AcademicObservationResponseSerializer
        ),
        401: openapi.Response(description="No autenticado. Token JWT ausente o inválido."),
        403: openapi.Response(
            description="Acceso denegado. El docente no es dueño de la observación solicitada.",
            examples={"application/json": {"error": "No tiene permisos para consultar esta observación académica."}}
        ),
        404: openapi.Response(
            description="La observación solicitada no existe en el repositorio.",
            examples={"application/json": {"error": "Observación con id 450 no encontrada."}}
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={"application/json": {"error": "Error interno del servidor"}}
        )
    }
)
@api_view(["GET"])
@permission_classes([IsAdminPsychologistOrTeacher])
def observation_detail(request, observation_id: int):
    """
    GET /api/observations/<observation_id>/

    Detalle de una observación.
    RN-10: Docente recibe vista restringida
           y solo puede acceder a sus propias observaciones.
    """
    requester_id, requester_role = _get_token_data(request)

    try:
        use_case = GetObservationUseCase(observation_repository)

        observation = (
            use_case.execute(observation_id=observation_id, requester_id=requester_id, requester_role=requester_role)
        )

        logger.info(
            f"[EVALUATION DETAIL] "
            f"evaluation_id={observation_id}"
        )

        serializer = (
            AcademicObservationResponseSerializer(observation)
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )
    
    except ObservationNotFoundError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_404_NOT_FOUND,
        )

    except ObservationAccessDeniedError as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_403_FORBIDDEN,
        )

    except Exception:
        logger.exception(
            "[UNEXPECTED ERROR] observation_detail"
        )

        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

# CU-07: HISTORIAL LONGITUDINAL

@swagger_auto_schema(
    method='get',
    operation_summary="Obtener historial longitudinal e integral del estudiante",
    operation_description=(
        "Recupera el expediente cronológico e integral de un estudiante mediante su ID. "
        "Docente (Vista Restringida): Solo visualiza el arreglo de observaciones académicas y información NEE general"
        "Flujos Alternativos:"
        "Si el estudiante existe pero no posee historial previo, se retornará "
        "un código HTTP 200 con la bandera `has_records: false` y los contadores en cero."
    ),
    responses={
        200: openapi.Response(
            description="Historial longitudinal recuperado. La estructura varía internamente según el rol.",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "student_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID único del estudiante."),
                    "student_info": openapi.Schema(
                        type=openapi.TYPE_OBJECT, 
                        description="Información demográfica básica del estudiante provista por el microservicio."
                    ),
                    "has_records": openapi.Schema(
                        type=openapi.TYPE_BOOLEAN, 
                        description="Indica si el estudiante posee registros en el historial académico/psicológico."
                    ),
                    "characterizations": openapi.Schema(
                        type=openapi.TYPE_OBJECT, 
                        description="Detalle o tipos de NEE según el nivel de acceso del rol solicitante."
                    ),
                    "follow_up_status": openapi.Schema(
                        type=openapi.TYPE_STRING, 
                        description="Estado de seguimiento según (ej: pendiente). Nulo para Docentes."
                    ),
                    "days_until_next_evaluation": openapi.Schema(
                        type=openapi.TYPE_INTEGER, 
                        description="Días restantes para la próxima reevaluación. Nulo para Docentes."
                    ),
                    "evaluations": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                        description="Colección de evaluaciones psicológicas. Vacío si el rol es Docente."
                    ),
                    "observations": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_OBJECT),
                        description="Lista de observaciones pedagógicas y de aula."
                    ),
                    "total_evaluations": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total de evaluaciones encontradas."),
                    "total_observations": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total de observaciones encontradas.")
                }
            ),
        ),
        401: openapi.Response(description="No autenticado. Credenciales JWT ausentes o expiradas."),
        403: openapi.Response(description="No autorizado. El rol del usuario no pertenece a la terna permitida."),
        404: openapi.Response(
            description="**EX-01:** El estudiante solicitado no existe en la base de datos centralizada de matrículas.",
            examples={
                "application/json": {
                    "error": "Estudiante con ID 999 no encontrado.",
                    "suggestion": "Verifique el número de documento del estudiante"
                }
            }
        ),
        502: openapi.Response(
            description="Error de pasarela. El microservicio de estudiantes no responde o devolvió un formato inesperado."
        ),
        500: openapi.Response(
            description="Error interno del servidor.",
            examples={"application/json": {"error": "Error interno del servidor"}}
        )
    }
)
@api_view(["GET"])
@permission_classes([IsAdminPsychologistOrTeacher])
def longitudinal_history(request, student_id: int):
    """
    GET /api/history/<student_id>/

    CU-07: Perfil integral e historial longitudinal del estudiante.

    Vista según rol (RN-10):
    - Psicólogo / Admin: perfil completo
        → evaluaciones psicológicas
        → observaciones académicas (detalle completo)
        → caracterizaciones NEE (detalle clínico)
        → estado de seguimiento (RN-11)

    - Docente: vista restringida
        → solo observaciones académicas (sin notas conductuales sensibles)
        → tipos de NEE (sin detalle clínico)
        → sin evaluaciones psicológicas

    Errores:
    - EX-01 → 404 estudiante no encontrado
    - EX-02 → 200 con has_records=False si no hay registros
    """
    _, requester_role = _get_token_data(request)

    try:
        history = get_longitudinal_history_use_case.execute(
            student_id=student_id,
            requester_role=requester_role,
        )

        logger.info(
            f"[LONGITUDINAL HISTORY] "
            f"student_id={student_id} "
            f"role={requester_role}"
        )

        evaluations_serializer = (
            PsychologicalEvaluationResponseSerializer(
                history.evaluations,
                many=True
            )
        )

        observations_serializer = AcademicObservationResponseSerializer(
            history.observations,
            many=True
        )

        return Response(
            {
            "student_id": history.student_id,
            "student_info": history.student_info, 
            "has_records": history.has_records,
            "characterizations": history.characterizations,
            "follow_up_status": history.follow_up_status,
            "days_until_next_evaluation": history.days_until_next_evaluation,

            "evaluations": evaluations_serializer.data,

            "observations": observations_serializer.data,

            "total_evaluations": history.total_evaluations,
            "total_observations": history.total_observations,
            },
            status=status.HTTP_200_OK
        )

    except StudentNotFoundError as e:
        # EX-01: El estudiante no existe en student-service
        return Response(
            {
                "error": str(e),
                "suggestion": "Verifique el número de documento del estudiante",
            },
            status=status.HTTP_404_NOT_FOUND,
        )
    except ExternalServiceError as e:
        return _service_error_response(e)

    except Exception:

        logger.exception(
            "[UNEXPECTED ERROR] longitudinal_history"
        )

        return Response(
            {"error": "Error interno del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


# HEALTH CHECK

@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /health/
    Estado del evaluation-service para Docker y NGINX.
    """
    return Response(
        {
            "status": "healthy",
            "service": "evaluation-service",
            "version": "1.0.0",
        },
        status=status.HTTP_200_OK,
    )