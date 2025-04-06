"""Base repository interfaces using Protocol."""

from typing import Generic, List, Optional, Protocol, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from ai_worthy_api_roo_1.database.models import Base

# Generic type variable for models
ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class BaseRepositoryProtocol(Protocol, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base repository protocol defining common operations."""

    async def get(self, id: int) -> Optional[ModelType]:
        """
        Get an entity by id.
        
        Args:
            id: The entity ID.
            
        Returns:
            The entity if found, None otherwise.
        """
        ...

    async def get_multi(
        self, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        Get multiple entities with pagination.
        
        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            
        Returns:
            List of entities.
        """
        ...

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Create a new entity.
        
        Args:
            obj_in: The data to create the entity with.
            
        Returns:
            The created entity.
        """
        ...

    async def update(
        self, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        """
        Update an entity.
        
        Args:
            db_obj: The database entity to update.
            obj_in: The update data.
            
        Returns:
            The updated entity.
        """
        ...

    async def delete(self, *, id: int) -> Optional[ModelType]:
        """
        Delete an entity.
        
        Args:
            id: The entity ID.
            
        Returns:
            The deleted entity if found, None otherwise.
        """
        ...