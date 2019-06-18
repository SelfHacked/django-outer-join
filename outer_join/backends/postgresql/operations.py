from django.db.backends.postgresql.operations import (
    DatabaseOperations as _PostgresqlDatabaseOperations,
)


class DatabaseOperations(_PostgresqlDatabaseOperations):
    compiler_module = 'outer_join.sql.compiler'
