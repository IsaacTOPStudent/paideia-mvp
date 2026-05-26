import pytest
from src.domain.exceptions import (
    DomainException,
    StudentAlreadyExistsError,
    StudentNotFoundError,
    InvalidStudentDataError,
    StudentNotReadyForCharacterizationError
)


class TestDomainExceptions:
    
    def test_student_already_exists_error(self):

        error = StudentAlreadyExistsError('1234567890')
        
        assert error.document == '1234567890'
        assert 'Ya existe un estudiante con documento: 1234567890' in str(error)
        assert isinstance(error, DomainException)
    
    def test_student_not_found_error(self):

        error = StudentNotFoundError('999')
        
        assert 'Estudiante no encontrado: 999' in str(error)
        assert isinstance(error, DomainException)
    
    def test_invalid_student_data_error(self):

        error = InvalidStudentDataError('Campos obligatorios faltantes')
        
        assert 'Campos obligatorios faltantes' in str(error)
        assert isinstance(error, DomainException)
    
    def test_student_not_ready_for_characterization_error(self):

        error = StudentNotReadyForCharacterizationError()
        
        assert 'perfil completo para caracterización' in str(error)
        assert isinstance(error, DomainException)