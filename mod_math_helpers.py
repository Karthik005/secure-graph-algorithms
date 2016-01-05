#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: karthik
# @Date:   2016-01-05 19:54:36

import numpy as np

def euclid(a, b):
	'''
	general euclidean algorithm
	@return		: coefficients of a,b in gcd
	'''
	if b > a:
		return euclid(b,a);
	elif b == 0:
		return (1, 0);
	else:
		(x, y) = euclid(b, a % b);
		return (y, x - (a / b) * y)

def find_inv_mod(a, p):
	'''
	find the modular inverse
	@arg		: num, modular base
	@return		: modular inverse of number
	'''
	a = a % p
	if (a == 0):
		return 0
	(x,y) = euclid(p, a % p);
	return y % p

def gen_identity_mat(n):
	'''
	generate identity matrix of dimensions n*n
	'''
	return [[long(x == y) for x in range(0, n)] for y in range(0, n)]

def find_inv_mat(matrix, q):
	'''
	find inverse modular inverse matrix
	@arg		: matrix, modular base
	@return		: inverse matrix (numpy matrix)
	'''
	n = len(matrix)
	A = np.matrix([[ matrix[j, i] for i in range(0,n)] for j in range(0, n)], dtype = long)
	Ainv = np.matrix(gen_identity_mat(n), dtype = long)
	for i in range(0, n):
		factor = find_inv_mod(A[i,i], q)
		A[i] = A[i] * factor % q
		Ainv[i] = Ainv[i] * factor % q
		for j in range(0, n):
			if (i != j):
				factor = A[j, i]
				A[j] = (A[j] - factor * A[i]) % q
				Ainv[j] = (Ainv[j] - factor * Ainv[i]) % q
	return Ainv