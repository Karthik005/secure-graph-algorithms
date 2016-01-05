#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: karthik
# @Date:   2016-01-05 19:54:36

import numpy as np

def generalizedEuclidianAlgorithm(a, b):
    if b > a:
        #print a, b
        return generalizedEuclidianAlgorithm(b,a);
    elif b == 0:
        return (1, 0);
    else:
        #print a,b
        (x, y) = generalizedEuclidianAlgorithm(b, a % b);
        return (y, x - (a / b) * y)

def inversemodp(a, p):
    a = a % p
    if (a == 0):
        print "a is 0 mod p"
        return 0
    (x,y) = generalizedEuclidianAlgorithm(p, a % p);
    return y % p

def identitymatrix(n):
    return [[long(x == y) for x in range(0, n)] for y in range(0, n)]

def inversematrix(matrix, q):
    n = len(matrix)
    A = np.matrix([[ matrix[j, i] for i in range(0,n)] for j in range(0, n)], dtype = long)
    Ainv = np.matrix(identitymatrix(n), dtype = long)
    for i in range(0, n):
        factor = inversemodp(A[i,i], q)
        A[i] = A[i] * factor % q
        Ainv[i] = Ainv[i] * factor % q
        for j in range(0, n):
            if (i != j):
                factor = A[j, i]
                A[j] = (A[j] - factor * A[i]) % q
                Ainv[j] = (Ainv[j] - factor * Ainv[i]) % q
                # print A, Ainv
                # print i, j, factor
    return Ainv