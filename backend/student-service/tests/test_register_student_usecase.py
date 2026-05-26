import pytest

from src.application.use_cases.register_student import RegisterStudentUseCase
from src.domain.entities.student import Student
from src.domain.exceptions import (
    StudentAlreadyExistsError,
    InvalidStudentDataError
)

class TestRegisterStudentUseCase:
    """Tests del caso de uso de registro de estudiante"""
    
    @pytest.fixture
    def use_case(self, mock_student_repository):
        return RegisterStudentUseCase(mock_student_repository)
    
    def test_register_student_success(self, use_case, mock_student_repository, valid_student_data):

        # Configurar mock
        mock_student_repository.exists_by_document.return_value = False
        mock_student_repository.save.return_value = Student(**valid_student_data)
        
        # Ejecutar
        result = use_case.execute(valid_student_data)
        
        # Verificar
        assert result is not None
        assert result.document_number == '1234567890'
        assert result.first_name == 'Juan'
        
        # Verificar que se llamó al repositorio
        mock_student_repository.exists_by_document.assert_called_once_with('1234567890')
        mock_student_repository.save.assert_called_once()
    
    def test_register_student_duplicate_document_raises_error(
        self, 
        use_case, 
        mock_student_repository, 
        valid_student_data
    ):
        # Configurar mock para simular documento existente
        mock_student_repository.exists_by_document.return_value = True
        
        # Verificar que lanza excepción
        with pytest.raises(StudentAlreadyExistsError):
            use_case.execute(valid_student_data)
        
        # Verificar que NO se llamó a save
        mock_student_repository.save.assert_not_called()
    
    def test_register_student_without_consent_raises_error(
        self, 
        use_case, 
        mock_student_repository, 
        student_without_consent
    ):
        # Configurar mock
        mock_student_repository.exists_by_document.return_value = False
        
        # Verificar que lanza excepción
        with pytest.raises(
            InvalidStudentDataError, 
            match="consentimiento informado del acudiente"
        ):
            use_case.execute(student_without_consent)
        
        # Verificar que NO se llamó a save
        mock_student_repository.save.assert_not_called()
    
    def test_register_student_missing_required_fields_raises_error(
        self, 
        use_case, 
        mock_student_repository, 
        student_missing_required_fields
    ):
        # Configurar mock
        mock_student_repository.exists_by_document.return_value = False
        
        # Verificar que lanza excepción
        with pytest.raises(
            InvalidStudentDataError, 
            match="Campos obligatorios faltantes"
        ):
            use_case.execute(student_missing_required_fields)
        
        # Verificar que NO se llamó a save
        mock_student_repository.save.assert_not_called()
    
    def test_register_student_trims_whitespace(
        self, 
        use_case, 
        mock_student_repository, 
        valid_student_data
    ):
        # Datos con espacios en blanco
        data = valid_student_data.copy()
        data['first_name'] = '  Juan  '
        data['document_number'] = '  1234567890  '
        
        # Configurar mock
        mock_student_repository.exists_by_document.return_value = False
        
        saved_student = None
        def capture_save(student):
            nonlocal saved_student
            saved_student = student
            return student
        
        mock_student_repository.save.side_effect = capture_save
        
        # Ejecutar
        use_case.execute(data)
        
        # Verificar que se eliminaron espacios
        assert saved_student.first_name == 'Juan'
        assert saved_student.document_number == '1234567890'