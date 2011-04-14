'''Here what I want to do is to realize the algorithm of the 
transfer learning which was designed for the cross-domain collaborative filtering
for sparsity reduction'''

from random import *
from math import sqrt

#basic function

#initialize a matrix that each row has only a nonnegative integer and the others are all 0
def _matrix_init(row, column):
    matrix = []
    for i in range(0, row):
        matrix.append([])
        for j in range(0, column):
            matrix[i].append(0)
    return matrix

def _matrix_init_para(row, column, para):
     matrix = []
     for i in range(0, row):
         matrix.append([])
         for j in range(0, column):
             matrix[i].append(para)
     return matrix
    
def _init(row, column):
    matrix = _matrix_init(row, column)
    for k in range(0, row):
        location = randrange(0, column)
        num = randrange(1, 100)
        matrix[k][location] = num
    return matrix

def _init_binary(row, column):
    matrix = _matrix_init(row, column)
    for k in range(0, row):
        location = randrange(0, column)
        matrix[k][location] = 1
    return matrix

def _multiplication(U, V):
    n = len(U)
    m = len(U[0])
    k = len(V[0])
    result = _matrix_init(n, k)
    for i in range(0, n):
        for j in range(0, k):
            sum = 0
            for p in range(0, m):
                sum += U[i][p] * V[p][j]
            result[i][j] = sum
    return result
    
def _transpose(U):
    n = len(U)
    m = len(U[0])
    V = _matrix_init(m, n)
    for i in range(0, m):
        for j in range(0, n):
            V[i][j] = U[j][i]
    return V

#codebook construction

#what one iterative round does is to update the U, V and S that meet the needs  
#U[n][k], V[m][l], S[k][l], X[n][m]
def _update(U, V, S, X):
    n = len(U)
    k = len(U[0])
    m = len(V)
    l = len(V[0])
    k = len(S)
    uA = _multiplication(_multiplication(X, V), _transpose(S))
    uB = _multiplication(_multiplication(_multiplication(_multiplication(U, _transpose(U)), X), V), _transpose(S))
    vA = _multiplication(_multiplication(_transpose(X), U), S)
    vB = _multiplication(_multiplication(_multiplication(_multiplication(V, _transpose(V)), _transpose(X)), U), S)
    sA = _multiplication(_multiplication(_transpose(U), X), V)
    sB = _multiplication(_multiplication(_multiplication(_multiplication(_transpose(U), U), S), _transpose(V)), V)
    for ui in range(0, n):
        for uj in range(0, k):
            if uB[ui][uj] != 0:
                U[ui][uj] = U[ui][uj] * sqrt(float(uA[ui][uj])/(uB[ui][uj])) 
            else:
                U[ui][uj] = 0
    for vi in range(0, m):
        for vj in range(0, l):
            if vB[vi][vj] != 0:
                V[vi][vj] = V[vi][vj] * sqrt(float(vA[vi][vj])/(vB[vi][vj]))
            else:
                V[vi][vj] = 0
    for si in range(0, k):
        for sj in range(0, l):
            if sB[si][sj] != 0:
                S[si][sj] = S[si][sj] * sqrt(float(sA[si][sj])/(sB[si][sj]))
            else:
                S[si][sj] = 0
    result = []
    result.append(U)
    result.append(V)
    result.append(S)
    return result

def _iteration(U, V, S, X):
    para = _update(U, V, S, X)
    #just take a 20th-iterative round, or you can make a if-ondition that see wether U, V and S meet the needs
    #there is a dault here
    for i in range(0, 100):
        para = _update(para[0], para[1], para[2], X)
    return para

def _auxiliary(U):
    n = len(U)
    k = len(U[0])
    for i in range(0, n):
        for j in range(0, k):
            if U[i][j] != 0:
                U[i][j] = 1
    return U

#the main function of codebook construction
def _codebook(U, V, X):
    n = len(X)
    m = len(X[0])
    k = len(U[0])
    l = len(V[0])
    B = _multiplication(_multiplication(_transpose(U), X), V)
    One = _matrix_init_para(n, m, 1)
    C = _multiplication(_multiplication(_transpose(U), One), V)
    for i in range(0, k):
        for j in range(0, l):
            if C[i][j] != 0:
                B[i][j] = B[i][j]/C[i][j]
            else:
                B[i][j] = 0
    return B

#the main port of the codebook construction
def codebookconstruction(X, k ,l):
    n = len(X)
    m = len(X[0])
    U = _init(n, k)
    V = _init(m, l)
    S = _init(k, l)
    result = _iteration(U, V, S, X)
    Uaux = _auxiliary(result[0])
    Vaux = _auxiliary(result[1])
    print Uaux
    print Vaux
    codebook = _codebook(Uaux, Vaux, X)
    return codebook


#codebook transfer

def _findrowmin(X, B, V, wi):
    q = len(X[0])
    k = len(B)
    matrix1 = _multiplication(B, _transpose(V))
    matrix2 = _matrix_init(1, q)
    flag = -1
    min = -1 
    for j in range(0, k):
        for i in range(0, q):
            matrix2[0][i] = X[wi][i] - matrix1[j][i]
        data = _weightednorm(matrix2)
        if min > data:
            flag = j
            min = data
    return flag

def _findcolumnmin(X, B, U, wi):
    p = len(X)
    l = len(B[0])
    matrix1 = _multiplication(_transpose(U), B)
    matrix2 = _matrix_init(p, 1)
    flag = -1
    min = -1
    for j in range(0, l):
        for i in range(0, p):
            matrix2[i][0] = X[i][wi] - matrix1[i][j]
        data = _weightednorm(matrix2)
        if data > min:
            flag = j
            min = data
    return flag

def _weightednorm(U):
    n = len(U)
    m = len(U[0])
    sum = 0
    for i in range(0, n):
        for j in range(0, m):
            sum += (U[i][j]) * (U[i][j])
    return sum

def _target(U, ui, uj):
    m = len(U[0])
    for j in range(0, m):
        if j == uj:
            U[ui][j] = 1
        else:
            U[ui][j] = 0
    return U

def _weightingmatrix(U):
    n = len(U)
    m = len(U[0])
    W = _matrix_init(n, m)
    for i in range(0, n):
        for j in range(0, m):
            if U[i][j] != 0:
                W[i][j] = 1
    return W

def _targetmatrix(X, W, U, V, B):
    p = len(X)
    q = len(X[0])
    matrix = _multiplication(_multiplication(U, B), _transpose(V))
    for i in range(0, p):
        for j in range(0, q):
            if W[i][j] == 0:
                X[i][j] = matrix[i][j]
    return X

#the main port of codebook transfer
def codebooktransfer(X, B):
    p = len(X)
    q = len(X[0])
    k = len(B)
    l = len(B[0])
    V = _init_binary(q, l)
    #20 iterative rounds
    for t in range(0, 20):
        for i in range(0, p):
            pi = _findrowmin(X, B, V, i)
            U = _target(U, i, pi)
        for j in range(0, q):
            pj = _findcolumnmin(X, B, U, j)
            V = _target(V, j, pj)
    W = _weightingmatrix(X)
    X = _targetmatrix(X, W, U, V, B)
    return X

if __name__ == '__main__':
    a=_init(2,3)
    b=_init(3,4)
    c=_multiplication(a, b)
    d=_transpose(a)
    print a
    print b
    e=_update(a, b, b, a)
    print a
    print b
    print e
