from transfer import codebookconstruction, codebooktransfer
import sqlite3

TABLE_NAME = 'core_rating_'
AUX_DB_FILE = 'eachmovie.db'
TAR_DB_FILE = 'recsys.sqlite3'
USER_SIZE = 500
MOVIE_SIZE = 500


conn = sqlite3.connect(AUX_DB_FILE)
conn2 = sqlite3.connect(TAR_DB_FILE)

def _getauxmatrix(intensity):
    matrix = []
    tablename = TABLE_NAME + str(intensity)
    user = conn.execute('SELECT distinct(user_id) from %s' % tablename).fetchall()
    movie = conn.execute('SELECT distinct(movie_id) from %s' % tablename).fetchall()
    flag = 0
    for u in user:
        matrix.append([])
        for m in movie:
            rating = conn.execute('SELECT rating from %s where user_id = %d and movie_id = %d' % (tablename, u[0], m[0])).fetchone()
            if rating != None:
                matrix[flag].append(rating[0])
            else:
                matrix[flag].append(0)
        flag += 1
    return matrix

def _gettarmatrix():
    matrix = []
    test = []
    res = conn2.execute('SELECT user_id, movie_id, rating from core_rating').fetchall()
    from random import random
    lenth = len(res)
    num = int(0.8 * lenth)
    while len(res) != num:
        pop = res.pop(int(random() * len(res)))
        test.append(pop)
    user = conn2.execute('SELECT distinct(user_id) from core_rating').fetchall() 
    movie = conn2.execute('SELECT distinct(movie_id) from core_rating').fetchall() 
    for i in range(0, len(user)):
        matrix.append([])
        for j in range(0, len(movie)):
            matrix[i].append(0)
    for r in res:
        matrix[r[0] - 1][r[1] - 1] = r[2] 
    return matrix, test


    
def transfer(intensity):
    matrix = _getauxmatrix(intensity)
    codebook = codebookconstruction(matrix, len(matrix), len(matrix[0]))
    res = codebooktransfer(_gettarmatrix(), codebook)
    return res


if __name__ == '__main__':
    a = _gettarmatrix()
    print a[0]
    print a[1]
