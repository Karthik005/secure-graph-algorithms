import sys
from math import log
import os

def rand_prime(n):
	# Returns an n-bit prime number
	while True:
		p = randrange(2**n + 1, 2**(n+1), 2)
		if all(p % m != 0 for m in range(3, int((p ** 0.5) + 1), 2)):
			return p

'''
 Function to generate a random t-degree polynomial with given constant
  @arg		: t:int, s:int, N:int
  @returns	: (pseudo) random t-degree polynomial function encoding secret `s'
'''
def gen_rand_poly(t, s, N):
	coefs = [s % N]
	bits = int(log(N) / log(2))
	# Choose `t' random numbers to be coefficients
	for i in range(1,t+1):
		# Get a sequence of random bytes
		rand_no = os.urandom(int(bits / 8))
		# Convert these bytes into an integer
		coef = sum([ord(rand_no[j]) * 2**j for j in range(0, len(rand_no))]) % N
		coefs.append(coef)
	def rand_poly_internal(x):
		f_x = 0
		for i in range(0, len(coefs)):
			f_x = ( f_x + (x**i) * coefs[i] ) % N
		return f_x
	return rand_poly_internal

'''
 Function to generate `n' shares of `s' with a threshold of `t'
  @arg		: n:int, t:int, s:int, N:int
  @returns	: list of shares
'''
def gen_shares(n, t, s, N):
	# Generate the encoding polynomial
	f = gen_rand_poly(t, s, N)
	# Generate each party's share
	shares = [(i, f(i)) for i in range(1, n+1)]
	return shares


'''
 Function to interpolate a t-degree polynomial given t+1 points
  @arg		: sh:[(x:int,f(x):int)], N:int
  @returns	: function containing t-degree polynomial passing through
  		  given points
'''
def interpolate_poly(sh, N):
	def inner_poly(a):
		# Find f(a)
		terms = []
		for s in sh:
			# List shares other than `s'
			other_sh = list(sh)
			other_sh.remove(s)
			# Lagrangian interpolation
			term = s[1]
			for shr in other_sh:
				# NOTE: Since finding modulo inverse takes a while,
				# floating point arithmetic is used as an approximation
				term = term * float((a-shr[0])) / (s[0]-shr[0])
			terms.append(term)
		return sum(terms) % N
	return inner_poly


# Test the sharing scheme for all numbers until any prime N
t = 3
N = 104059
offset = 2
for i in range(0, N):
	secret = i
	sh = gen_shares(6, t, secret, N)
	f = interpolate_poly(sh[offset:t+1+offset], N)
	if f(0) == secret:
		print "PASS", f(0)
	else:
		print "FAIL, " + str(i) + ", " + str(f(0)) + ", " + str(f(0)-i)
