import os
import psycopg2
from dotenv import load_dotenv
import logging

load_dotenv()


class FSTRDatabase:
    def __init__(self):
        self.host = os.getenv("FSTR_DB_HOST")
        self.port = os.getenv("FSTR_DB_PORT")
        self.user = os.getenv("FSTR_DB_LOGIN")
        self.password = os.getenv("FSTR_DB_PASS")
        self.database = os.getenv("FSTR_DB_NAME", "fstr_db")
        self.conn = None
        self.cursor = None
        try:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
            print("Connected to the database successfully!")
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def __del__(self):
        if self.conn:
            self.cursor.close()
            self.conn.close()
            print("Disconnected from database.")

    def execute_query(self, query, *params):
        try:
            self.cursor.execute(query, params)
            self.conn.commit()
            result = self.cursor.fetchall()
            if result and result[0]:
                return result[0][0]
            else:
                return None
        except psycopg2.Error as e:
            logging.error(f"Database query error: {e} with params {params} and query: {query}")
            self.conn.rollback()
            return None

    def add_user(self, email, fam=None, name=None, otc=None, phone=None):
        sql = "INSERT INTO users (email, fam, name, otc, phone) VALUES (%s, %s, %s, %s, %s) RETURNING id"
        user_id = self.execute_query(sql, email, fam, name, otc, phone)
        return user_id

    def add_coord(self, latitude, longitude, height):
        sql = "INSERT INTO coords (latitude, longitude, height) VALUES (%s, %s, %s) RETURNING id"
        coord_id = self.execute_query(sql, latitude, longitude, height)
        return coord_id

    def add_levels(self, winter, summer, autumn, spring):
        sql = "INSERT INTO levels (winter, summer, autumn, spring) VALUES (%s, %s, %s, %s) RETURNING id"
        level_id = self.execute_query(sql, winter, summer, autumn, spring)
        return level_id

    def add_pereval(self, user_id, coord_id, level_id, date_added, beauty_title, title, other_titles, connect):
        sql = "INSERT INTO perevals (user_id, coord_id, level_id, date_added, beauty_title, title, other_titles, connect, add_time, status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), 'new') RETURNING id"
        pereval_id = self.execute_query(sql, user_id, coord_id, level_id, date_added, beauty_title, title, other_titles, connect)
        return pereval_id

    def add_image(self, img_data):
        sql = "INSERT INTO images (img) VALUES (%s) RETURNING id"
        img_id = self.execute_query(sql, (psycopg2.Binary(img_data),))
        return img_id

    def add_pereval_image(self, pereval_id, image_id):
        sql = "INSERT INTO pereval_images (pereval_id, image_id) VALUES (%s, %s)"
        return self.execute_query(sql, pereval_id, image_id)