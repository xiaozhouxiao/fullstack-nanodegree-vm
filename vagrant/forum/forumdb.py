# "Database code" for the DB Forum.

import psycopg2, bleach

## Get posts from database.
def get_posts():
    DB = psycopg2.connect(database="forum")
    c = DB.cursor()
    c.execute('''
        delete from posts where content like '%spam%'
        ''')
    c.execute("SELECT content, time FROM posts ORDER BY time DESC")
    posts = c.fetchall()
    DB.close()
    return posts

## Add a post to the database.
def add_post(content):
    DB = psycopg2.connect(database="forum")
    c = DB.cursor()
    c.execute("INSERT INTO posts VALUES (%s)", (bleach.clean(content),))
    DB.commit()
    DB.close()
