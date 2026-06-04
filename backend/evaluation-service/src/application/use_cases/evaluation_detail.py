from src.domain.entities.psychological_evaluation import PsychologicalEvaluation
from src.domain.ports.psychological_evaluation_repository import PsychologicalEvaluationRepository

from src.domain.exceptions import EvaluationNotFoundError

class GetEvaluationUseCase:

    def __init__(self, repository: PsychologicalEvaluationRepository):
        self.repository = repository

    def execute(self, evaluation_id: int) -> PsychologicalEvaluation:

        evaluation = self.repository.find_by_id(evaluation_id)

        if not evaluation:
            raise EvaluationNotFoundError(evaluation_id)
        
        return evaluation