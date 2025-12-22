import uuid

import pytest

from src.domain.models.user import User
from src.domain.models.vote import Vote
from src.domain.schemas.user import UserCreate, UserUpdateName
from src.exceptions.base import NotFoundException
from src.services.user_service import UserMaintainService

pytestmark = pytest.mark.unit


class TestUserService:
    @pytest.fixture
    def user_service(self):
        return UserMaintainService()

    @pytest.fixture
    def sample_user(self):
        return User(id=uuid.uuid4(), name="Test User", is_deleted=False)

    @pytest.mark.asyncio
    async def test_user_created(self, user_service, mock_uow, sample_user):
        mock_uow.repositories[User].create.return_value = sample_user

        data = UserCreate(name="Test User")
        result = await user_service.create_user(mock_uow, data)

        assert result.name == "Test User"
        assert result.is_deleted is False

    @pytest.mark.asyncio
    async def test_user_name_updated_successfully(self, user_service, mock_uow, sample_user):
        user_id = sample_user.id
        updated_user = User(id=user_id, name="Name", is_deleted=False)

        mock_uow.repositories[User].get.return_value = sample_user
        mock_uow.repositories[User].update_name.return_value = updated_user

        data = UserUpdateName(name="Name")
        result = await user_service.change_username(mock_uow, user_id, data)

        assert result.name == "Name"

    @pytest.mark.asyncio
    async def test_deleting_nonexistent_user_raises_error(self, user_service, mock_uow):
        user_id = uuid.uuid4()
        mock_uow.repositories[User].get.return_value = None

        with pytest.raises(NotFoundException):
            await user_service.delete_user(mock_uow, user_id)

    @pytest.mark.asyncio
    async def test_user_vote_history_retrieved(self, user_service, mock_uow, sample_user):
        user_id = sample_user.id
        mock_votes = [
            (Vote(id=uuid.uuid4(), idea_id=uuid.uuid4(), user_id=user_id), "lol lol", uuid.uuid4()),
            (Vote(id=uuid.uuid4(), idea_id=uuid.uuid4(), user_id=user_id), "kek kek", uuid.uuid4()),
        ]

        mock_uow.repositories[User].get.return_value = sample_user
        mock_uow.repositories[Vote].get_user_votes.return_value = mock_votes

        result = await user_service.get_votes_history(mock_uow, user_id)

        assert len(result) == 2
