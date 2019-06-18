from django.db.backends.postgresql.base import (
    DatabaseWrapper as _PostgresqlDatabaseWrapper,
)

from .operations import DatabaseOperations


class DatabaseWrapper(_PostgresqlDatabaseWrapper):
    ops_class = DatabaseOperations
