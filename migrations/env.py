import asyncio
from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
from alembic import context

from aris_api.models import table_registry
from aris_api.settings import settings

# --- Configurações do Alembic ---
config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Configuração de logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata das tabelas (para autogenerate)
target_metadata = table_registry.metadata


# --- Execução offline ---
def run_migrations_offline() -> None:
    """Executa as migrações em modo offline."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- Execução online (modo assíncrono) ---
def do_run_migrations(connection):
    """Função síncrona chamada dentro do contexto assíncrono."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations_online() -> None:
    """Executa migrações em modo online (com banco real)."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Wrapper para rodar o modo assíncrono no asyncio.run."""
    asyncio.run(run_async_migrations_online())


# --- Execução principal ---
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

