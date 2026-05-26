import pytest
from src.application.use_cases.list_students import ListStudentsUseCase
from src.domain.entities.student import Student

class TestListStudentsUseCase:
    
    @pytest.fixture
    def use_case(self, mock_student_repository):
        return ListStudentsUseCase(mock_student_repository)
    
    def test_list_active_students_only(
        self, 
        use_case, 
        mock_student_repository, 
        student_entity,
        valid_student_data
    ):

        students = [student_entity, Student(**valid_student_data)]
        mock_student_repository.find_all.return_value = students

        result = use_case.execute(include_inactive=False)

        assert len(result) == 2
        mock_student_repository.find_all.assert_called_once()
        mock_student_repository.find_all_including_inactive.assert_not_called()
    
    def test_list_all_students_including_inactive(
        self, 
        use_case, 
        mock_student_repository, 
        student_entity,
        inactive_student_entity
    ):

        students = [student_entity, inactive_student_entity]
        mock_student_repository.find_all_including_inactive.return_value = students

        result = use_case.execute(include_inactive=True)
        
        assert len(result) == 2
        assert any(not s.is_active for s in result)  # Al menos uno inactivo
        mock_student_repository.find_all_including_inactive.assert_called_once()
        mock_student_repository.find_all.assert_not_called()
    
    def test_list_students_empty_result(self, use_case, mock_student_repository):

        mock_student_repository.find_all.return_value = []
        
        result = use_case.execute()
        
        assert result == []
        assert len(result) == 0