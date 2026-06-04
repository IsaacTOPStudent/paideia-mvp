from src.domain.entities.academic_observation import AcademicObservation
from src.domain.ports.academic_observation_repository import AcademicObservationRepository

from src.domain.exceptions import ObservationNotFoundError, ObservationAccessDeniedError

class GetObservationUseCase:

    def __init__(self, repository: AcademicObservationRepository):
        self.repository = repository

    def execute(self, observation_id: int, requester_id: int, requester_role: str) -> AcademicObservation:

        observation = self.repository.find_by_id(observation_id)

        if not observation: 
            raise ObservationNotFoundError(observation_id)
        
        if requester_role == "TEACHER" and observation.teacher_id != requester_id:
            raise ObservationAccessDeniedError()
        
        return observation