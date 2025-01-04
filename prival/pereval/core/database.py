import os
import psycopg2
from dotenv import load_dotenv
import logging
import base64

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
    def get_pereval_by_id(self, id):
        sql = "SELECT * FROM perevals WHERE id = %s"
        try:
            result = self.execute_query(sql, id)
            if result:
                 sql = "SELECT * FROM users WHERE id = %s"
                 user = self.execute_query(sql, result[1])
                 sql = "SELECT * FROM coords WHERE id = %s"
                 coord = self.execute_query(sql, result[2])
                 sql = "SELECT * FROM levels WHERE id = %s"
                 level = self.execute_query(sql, result[3])
                 sql = "SELECT image_id FROM pereval_images WHERE pereval_id = %s"
                 images_id = self.execute_query(sql, id)
                 images=[]
                 for image_id in images_id:
                    sql = "SELECT img FROM images WHERE id=%s"
                    img = self.execute_query(sql, image_id)
                    if img:
                       images.append(base64.b64encode(img).decode('utf-8'))

                 if user and coord and level:
                    return {
                        "user": user,
                        "coords": coord,
                        "levels": level,
                        "prival": result,
                        "images": images
                     }
                 else:
                     return None
            else:
               return None
        except Exception as e:
            logging.error(f"Error getting pereval by id: {e}")
            return None

    def get_perevals_by_user_email(self, email):
            sql = "SELECT * FROM users WHERE email = %s"
            try:
                user_id = self.execute_query(sql, email)
                if user_id:
                 sql = "SELECT * FROM perevals WHERE user_id = %s"
                 perevals = self.execute_query(sql, user_id)
                 return perevals
                else:
                  return None
            except Exception as e:
               logging.error(f"Error getting perevals by user email: {e}")
               return None
    def update_coord(self, id, latitude, longitude, height):
         sql = "UPDATE coords SET latitude = %s, longitude = %s, height = %s WHERE id = %s"
         try:
            self.execute_query(sql, latitude, longitude, height, id)
            return id
         except Exception as e:
             logging.error(f"Error updating coord: {e}")
             return None


    def update_levels(self, id, winter, summer, autumn, spring):
          sql = "UPDATE levels SET winter = %s, summer = %s, autumn = %s, spring = %s WHERE id = %s"
          try:
              self.execute_query(sql, winter, summer, autumn, spring, id)
              return id
          except Exception as e:
              logging.error(f"Error updating levels: {e}")
              return None

    def update_pereval(self, id, date_added, beauty_title, title, other_titles, connect):
        sql = "UPDATE perevals SET date_added = %s, beauty_title = %s, title = %s, other_titles = %s, connect = %s WHERE id = %s"
        try:
            self.execute_query(sql, date_added, beauty_title, title, other_titles, connect, id)
            return id
        except Exception as e:
             logging.error(f"Error updating pereval: {e}")
             return None
    def delete_pereval_images(self, id):
        sql = "DELETE FROM pereval_images WHERE pereval_id = %s"
        try:
           self.execute_query(sql, id)
        except Exception as e:
            logging.error(f"Error deleting pereval images: {e}")
            return None