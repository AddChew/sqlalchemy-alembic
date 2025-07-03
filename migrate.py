import os

from alembic import command
from alembic.config import Config

config_path = os.path.join(os.path.abspath(os.getcwd()), "migrations", "alembic.ini") 
alembic_config = Config(config_path)
command.upgrade(alembic_config, "head")