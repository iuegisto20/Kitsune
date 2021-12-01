import logging
from threading import Thread
from distutils.util import strtobool

from configs.env_vars import ENV_VARS, DERIVED_VARS
from src.internals.utils import indexer, key_watcher
from yoyo import get_backend, read_migrations

from src.internals.cache import redis
from src.internals.database import database
from src.lib import server

logging.basicConfig(filename='kemono_importer.log', level=logging.DEBUG)
logging.getLogger('requests').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)

database.init()
redis.init()

backend = get_backend(DERIVED_VARS.PG_URL)
migrations = read_migrations('./migrations')
with backend.lock():
    backend.apply_migrations(backend.to_apply(migrations))


Thread(target=indexer.run).start()
if (strtobool(ENV_VARS.PUBSUB)):
    Thread(target=key_watcher.watch).start()
Thread(target=server.run).start()
