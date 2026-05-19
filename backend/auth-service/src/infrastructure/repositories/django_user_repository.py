from typing import Optional, List
from datetime import datetime
from authentication.models import UserModel
from ...domain.entities.user import User, UserRole, UserStatus
from ...domain.ports.user_repository import UserRepository
from ...domain.exceptions import UserAlreadyExistsError

class DjangoUserRepository(UserRepository):
    """
    Adapter: Users repository implementation using Django ORM.
    Implements the UserRepository port
    """

    def save(self, user: User) -> User:
        """
            Save or update a user in the database.
        """
        try:
            if user.id:
                # Update existing user
                user_model = UserModel.objects.get(id=user.id)
                user_model.email = user.email
                user_model.full_name = user.full_name
                user_model.password = user.password_hash
                user_model.role = user.role.value
                user_model.status = user.status.value
                user_model.updated_at = user.updated_at
                user_model.save()
            else:
                # Create new user
                creator = None
                if user.created_by:
                    creator = UserModel.objects.get(pk=user.created_by)

                user_model = UserModel.objects.create(
                    email=user.email,
                    full_name=user.full_name,
                    password=user.password_hash,
                    role=user.role.value,
                    status=user.status.value,
                    created_by=creator
                )

                user.id = user_model.pk
            
            return self._to_entity(user_model)
        
        except Exception as e:
            if 'unique constraint' in str(e).lower() or 'duplicate' in str(e).lower():
                raise UserAlreadyExistsError(user.email)
            raise 

    def find_by_id(self, user_id: int) -> Optional[User]:
        """
        Find a user by their ID.
        """

        try: 
            user_model = UserModel.objects.get(id=user_id)
            return self._to_entity(user_model)
        except UserModel.DoesNotExist:
            return None
        
    def find_by_email(self, email: str) -> Optional[User]:
        """
        Find user by id
        """

        try:
            user_model = UserModel.objects.get(email=email)
            return self._to_entity(user_model)
        except UserModel.DoesNotExist:
            return None
        
    def find_all_active(self) -> List[User]:
        """
        Find all active users
        """

        user_models = UserModel.objects.filter(status='ACTIVE')
        return [self._to_entity(um) for um in user_models]
    
    def find_all(self) -> List[User]:
        """
        Find all users
        """

        user_models = UserModel.objects.all()
        return [self._to_entity(um) for um in user_models]
    
    def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists with the given email
        """
        return UserModel.objects.filter(email=email).exists()
    
    def deactivate(self, user_id: int) -> bool:
        """
        Deactivate a user by setting their status to INACTIVE
        """

        try:
            user_model = UserModel.objects.get(id=user_id)
            user_model.status = 'INACTIVE'
            user_model.updated_at = datetime.now()
            user_model.save()
            return True
        except UserModel.DoesNotExist:
            return False
        
    def reactivate(self, user_id: int) -> bool:
        """
            Reactivate a user by setting their status to ACTIVE
        """
        try: 
            user_model = UserModel.objects.get(id=user_id)
            user_model.status = 'ACTIVE'
            user_model.updated_at = datetime.now()
            user_model.save()
            return True
        except UserModel.DoesNotExist:
            return False

    @staticmethod   
    def _to_entity(user_model: UserModel) -> User:
        """
        Convert django model instance to domain entity
        """

        return User(
            id=user_model.pk,
            email=user_model.email,
            full_name=user_model.full_name,
            password_hash=user_model.password,
            role=UserRole.from_str(user_model.role),
            status=UserStatus.from_str(user_model.status),
            created_at=user_model.created_at,
            updated_at=user_model.updated_at,
            created_by=user_model.created_by
        )
        