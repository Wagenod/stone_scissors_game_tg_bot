from enum import Enum

import pickledb
from config import STATS_DB


class DatabaseTables(Enum):
    GIF_ID_TABLE = "gif_id"
    STATS_TABLE = "stats"


class GameResult(Enum):
    VICTORY = "victory"
    DEFEAT = "defeat"


class Database:
    def __init__(self):
        self.db = pickledb.load(STATS_DB, False)
        if not self.db.getall(): #db is empty
            self.__init_db()

    def __init_db(self):
        self._create_gif_id_table()
        self._create_stats_table()

    def _create_gif_id_table(self):
        self.db.dcreate(DatabaseTables.GIF_ID_TABLE)
        for result_name in GameResult:
            self.db.dadd(DatabaseTables.GIF_ID_TABLE, (result_name, None))

    def _create_stats_table(self):
        self.db.dcreate(DatabaseTables.STATS_TABLE)

    def dump(self):
        self.db.dump()


db = Database()
for result_name in GameResult:
    print(result_name)
print(db.db.dget("gif_id", GameResult.VICTORY))