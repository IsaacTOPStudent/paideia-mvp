from dataclasses import dataclass
from typing import Any, Optional, List

@dataclass
class LongitudinalHistoryResult:
    student_id: int

    student_info: dict 

    characterizations: List[dict]

    follow_up_status: Optional[str]
    days_until_next_evaluation: Optional[int]

    evaluations: list 
    observations: list 

    total_evaluations: int
    total_observations: int 

    has_records: bool