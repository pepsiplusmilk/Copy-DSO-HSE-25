from typing import Any, Callable, Type


class DBWorkUnit:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

        self.repositories: dict[Type, Any] = {}
        self._repos: dict[Type, Callable] = {}

    def register_repository(self, value_type: Type, repository: Callable):
        self._repos[value_type] = repository

    async def __aenter__(self):
        self.session = self.session_factory()

        for value_type, repo in self._repos.items():
            self.repositories[value_type] = repo(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    @classmethod
    def create_with_repositories(cls, session_factory, repositories: dict[Type, Callable]):
        instance = cls(session_factory)
        for value_type, repo in repositories.items():
            instance.register_repository(value_type, repo)
        return instance
