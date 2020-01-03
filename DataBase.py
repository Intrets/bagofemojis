import pickle
import sqlite3


class DataBase():

    def __init__(self, database):
        self.database = database
        self.create_table()

    def create_table(self):
        db = sqlite3.connect(self.database)
        db.execute('''
            CREATE TABLE IF NOT EXISTS users (user_id int PRIMARY KEY, display_name varchar(255), points integer, kills integer)
            ''')
        db.close()

    def load_from_files(self):
        file = open('goodpoints', "rb")
        namPoints = pickle.load(file)
        file.close()
        try:
            db = sqlite3.connect(self.database)

            prepare = []
            for (user, value) in namPoints.items():
                prepare.append((user, value[0], value[1], 0))
            with db:
                db.executemany('''
                    INSERT INTO users VALUES (?,?,?,?)
                    ''', prepare)
            db.close()
        except:
            print('failed db')

    def test(self):
        db = sqlite3.connect(self.database)
        with db:
            db.execute('''
                UPDATE users 
                SET kills = ? 
                WHERE display_name = 'N_888'
                ''', (str(93),))
        db.close()

    def get_by_ID(self, user_id: int):
        try:
            db = sqlite3.connect(self.database)
            res = db.execute('''
                SELECT * FROM users 
                WHERE user_id = ?
                ''', (user_id,))
            data = res.fetchone()
            db.close()
        except:
            print('get_by_ID exception')
            data = None
        return (data)

    def get_by_display(self, display_name: str):
        try:
            db = sqlite3.connect(self.database)
            res = db.execute('''    
                SELECT * FROM users 
                WHERE display_name = ? 
                ''', (display_name,))
            data = res.fetchone()
            db.close()
        except:
            print('get_by_display exception')
            data = None
        return (data)

    def get_total_kills(self):
        try:
            db = sqlite3.connect(self.database)
            res = db.execute('''
                SELECT SUM(kills)
                FROM users
                ''')
            data = res.fetchone()[0]
            db.close()
        except:
            print('get_total_kill exception')
            data = None
        return (data)

    def get_top_points(self, limit=1):
        try:
            db = sqlite3.connect(self.database)
            res = db.execute('''
                SELECT *
                FROM users
                ORDER BY points DESC
                LIMIT ?
                ''', (limit,))
            data = res.fetchall()
            db.close()
        except:
            print('get_top_points exception')
            data = None
        return (data)

    def get_top_kills(self, limit=1):
        try:
            db = sqlite3.connect(self.database)
            res = db.execute('''    
                SELECT *
                FROM users
                ORDER BY kills DESC
                LIMIT ?
                ''', (limit,))
            data = res.fetchall()
            db.close()
        except:
            print('get_top_kills exception')
            data = None
        return (data)

    def add_points_id(self, id, points):
        try:
            db = sqlite3.connect(self.database)
            with db:
                res = db.execute(''' 
                    UPDATE users
                    SET points = points + ?
                    WHERE user_id = ?
                    ''', (points, id))
            db.close()
        except:
            return False
        return True

    def add_points_display(self, display, points):
        try:
            db = sqlite3.connect(self.database)
            with db:
                res = db.execute(''' 
                    UPDATE users
                    SET points = points + ?
                    WHERE display_name = ?
                    ''', (points, display))
            db.close()
        except:
            return False
        return True

    def add_user(self, id, display, points=0, kills=0):
        try:
            db = sqlite3.connect(self.database)
            with db:
                res = db.execute('''
                    INSERT INTO users
                    VALUES (?,?,?,?)
                    ''', (id, display, points, kills))
            db.close()
        except:
            return False
        return True

    def reset_user_points(self, user_id):
        try:
            db = sqlite3.connect(self.database)
            with db:
                res = db.execute('''
                UPDATE users
                SET points = 0
                WHERE user_id = ?
                ''', (user_id,))
            db.close()
        except:
            return False
        return True

    def add_kills_id(self, user_id, kills):
        try:
            db = sqlite3.connect(self.database)
            with db:
                res = db.execute(''' 
                    UPDATE users
                    SET kills = kills + ?
                    WHERE user_id = ?
                    ''', (kills, user_id))
            db.close()
        except:
            return False
        return True

# d = DataBase()
# # d.create_table()
# # d.load_from_files()
# print(d.get_by_display('Intrets__'))
# d.add_points_display('Intrets__', 1)
# print(d.get_by_display('Intrets__'))
#
# print(d.get_by_ID(86679158))
