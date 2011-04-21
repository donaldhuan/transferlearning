# HOWTO USE:
#   "python mine.py" will show the intense value
#   "python mine.py 1" will create a new table of selecting users and movies

# CONFIG
USER_SIZE = 74424
MOVIE_SIZE = 1648
TAR_USER_SIZE = 500
TAR_MOVIE_SIZE = 500
DB_FILE = 'eachmovie.db'
TABLE_NAME = 'core_rating_'
CACHE_FILE = 'cache'
USER_START = 0  # modify this pair to change intensity
MOVIE_START = 0
# init
import sqlite3
conn = sqlite3.connect(DB_FILE)

def mine():
    '''mine aims at mining a sub-matrix with random algorithm'''
    users = range(1, USER_SIZE + 1)
    movies = range(1, MOVIE_SIZE + 1)
    users = _random_pop(users, TAR_USER_SIZE)
    movies = _random_pop(movies, TAR_MOVIE_SIZE)
    return users, movies

def _random_pop(lst, num):
    '''randomly pop elements in lst until len(lst) == num'''
    from random import random
    while len(lst) != num:
        lst.pop(int(random() * len(lst)))
    return lst

def mine2(usrstrt = 0, mvstrt = 0):
    '''attempt to mining the most intense sub-matrix by finding the most active users and movies
    usrstrt -> the function will return [user_start: user_start + TAR_USER_SIZE]
    mvstrt -> just as mentioned before'''
    import cPickle
    try:
        users, movies = cPickle.loads(open(CACHE_FILE).read())
    except IOError, e:
        users = conn.execute('SELECT user_id, count(*) as c FROM core_rating GROUP BY user_id ORDER BY c DESC').fetchall()
        movies = conn.execute('SELECT movie_id, count(*) as c FROM core_rating GROUP BY movie_id ORDER BY c DESC').fetchall()
        users = [u[0] for u in users]
        movies = [m[0] for m in movies]
        open(CACHE_FILE, 'w').write(cPickle.dumps((users, movies)))
    return users[usrstrt: usrstrt + TAR_USER_SIZE], movies[mvstrt: mvstrt + TAR_MOVIE_SIZE]
    

def evaluate(users, movies):
    '''evaluate the intensity of a sub-matrix determined by (users, movies)'''
    hit = 0
    rs = conn.execute('SELECT user_id, movie_id FROM core_rating WHERE user_id IN %s' % str(tuple(users))).fetchall()
    for r in rs:
        if r[1] in movies:
            hit += 1
    return hit * 1.0 / (len(users) * len(movies)) 

if __name__ == '__main__':
    from sys import argv, exit
    users, movies = mine2(USER_START, MOVIE_START)
    intensity = evaluate(users, movies)
    if len(argv) == 2 and argv[1] == '1':
        TABLE_NAME += str(int(intensity * 100))
        conn.execute('''CREATE TABLE "%s" (
            "id" integer NOT NULL PRIMARY KEY,
                "user_id" integer NOT NULL REFERENCES "core_user" ("id"),
                    "movie_id" integer NOT NULL REFERENCES "core_movie" ("id"),
                        "rating" integer NOT NULL,
                            "timestamp" datetime NOT NULL
                            );''' % TABLE_NAME)
        conn.execute('CREATE INDEX "%s_403f60f" ON "%s" ("user_id");' % (TABLE_NAME, TABLE_NAME))
        conn.execute('CREATE INDEX "%s_5d0896af" ON "%s" ("movie_id");' % (TABLE_NAME, TABLE_NAME))
        conn.execute('INSERT INTO %s SELECT * FROM core_rating WHERE user_id IN %s AND movie_id IN %s' % (TABLE_NAME, str(tuple(users)), str(tuple(movies))))
        conn.commit()
    else:
        print intensity
