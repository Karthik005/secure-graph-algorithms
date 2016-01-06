#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: karthik
# @Date:   2016-01-02 19:30:08

'''
Module to handle arithmetic black box functions
'''

import shamir_sharing as ss
import numpy as np
import net_share as ns
import net_recv as nr
import mod_math_helpers as mmh
from random import randint
from libnum import jacobi
from math import log, floor

# def signal_done_proc(prev_party,nxt_party, sig):
# 	if prev_party:
# 		recvd = soh.recv_sig(prev_party)
# 		if recvd == sig:
# 			if nxt_party:
# 				soh.send_sig(nxt_party, sig)
# 			return

'''
 Function to simply negate a share
  @arg		: share of x, N
  @returns	: share of -x
'''
def neg(sh, N):
	return (sh[0], N-sh[1])


def add(self_pid, socket_list, addend_shares, N):
	'''
	add shares listed in addend_shares
	@arg		: self party id, list of sockets, list of shares to be added, prime base
	@returns 	: sum of shares
	'''

	num_parties = len(socket_list)
	sum_of_shares = sum([addend_share[1] for addend_share in addend_shares])%N

	# done_msg = "ADDDONE"
	# nxt_party = socket_list[self_pid] if self_pid < num_parties else None
	# prev_party = socket_list[self_pid-1] if self_pid != 1 else None

	return (self_pid, sum_of_shares)


def gen_vandermonde(n):
	'''
	generates an nxn vandermond matrix
	@arg		: number of parties
	@returns 	: nxn vandermonde matrix
	'''
	vandermonde = np.array([[i**(j-1) for j in range(1,n+1)] for i in range(1,n+1)])
	return vandermonde

def gen_coeff_arr(n, N):
	'''
	generates reduction array
	@arg		: number of parties, number of corrupted parites (max)
	@returns 	: degree reduction array
	'''
	# trunc_arr = np.concatenate((np.ones(t),np.zeros(n-t)))
	# print B
	# print B_inv
	# red_arr = np.dot(np.dot(B,trunc_arr),B_inv)
	# return red_arr
	B = gen_vandermonde(n)
	B_inv = mmh.find_inv_mat(B, N)
	# print np.array(B_inv[0])
	return (np.array(B_inv[0])).flatten()

	

def mult(self_pid, socket_list, mult_shares, t, N, nB):
	'''
	multiply shares listed in mult_shares
	@arg		: self party id, list of party sockets, tuple of shares to be multiplied, prime base, share size
	@returns 	: product share
	'''
	n = len(socket_list)

	# generate self share
	x_self,y_self = mult_shares[0][1], mult_shares[1][1]
	prod = x_self * y_self % N
	z_self = (self_pid, prod)

	# print "z val: ", z_self
	#randomisation step
	h_shares = ss.gen_shares(n, t, z_self[1], N)
	ns.distribute_secret(h_shares, socket_list, nB)
	h_recvd_shares = nr.recv_shares(socket_list, nB)
	h_recvd_shares[self_pid-1] = h_shares[self_pid-1]
	h_recvd_shares_vals = [i[1] for i in h_recvd_shares]

	h_recvd_vals = np.array(h_recvd_shares_vals)
	coeff_arr = gen_coeff_arr(n,N)

	# print "coeff_arr: ", coeff_arr
	self_mult_share = np.dot(h_recvd_vals, coeff_arr)

	return (self_pid, self_mult_share % N)


def rec_mult(self_pid, socket_list, mult_shares, t, N, nB ):
	'''
	calculate recursively the product of all shares in mult_shares
	@arg		: self party id, list of party sockets, list of shares to be multiplied, prime base,
				  share size
	@returns 	: share of product
	'''
	num_shares = len(mult_shares)
	if num_shares %2 == 0:
		if num_shares == 2:
			return mult(self_pid, socket_list, mult_shares, t, N, nB)
		else:
			k_1 = rec_mult(self_pid, socket_list, mult_shares[:num_shares/2], t, N, nB)
			k_2 = rec_mult(self_pid, socket_list, mult_shares[num_shares/2:], t, N, nB)
			return mult(self_pid, socket_list, (k_1, k_2), t, N, nB)
	else:
		k_1 = rec_mult(self_pid, socket_list, mult_shares[:-1], t, N, nB)
		k_2 = mult_shares[-1]
		return mult(self_pid, socket_list, (k_1, k_2), t, N, nB)


def test_equality_once(self_pid, socket_list, comp_shares, t, N, nB, act_parties):
	'''
	test equality of two shared secrets, can give false positives with probability 1/2
	@arg		: self party id, list of party sockets, tuple of shares to be compared, prime base,
				  share size, pids of contributing parties
	@returns 	: share of equality boolean x==y
	'''
	n = len(socket_list)
	x,y = comp_shares
	d = add(self_pid, socket_list, (x,neg(y,N)), N)[1]
	x,y = x[1], y[1]

	A,B = act_parties # index of contributing parties
	party_A = socket_list[A-1]
	party_B = socket_list[B-1]

	# obtain random input shares
	if self_pid in act_parties:
		r_i = randint(1,N-1)
		r_shares = ss.gen_shares(n, t, r_i, N)
		ns.distribute_secret(r_shares, socket_list, nB)
		r_a = r_shares[self_pid-1][1]
		party_other_pid = [i for i in act_parties if i!=self_pid][0]
		party_other = socket_list[party_other_pid-1]
		r_b = nr.recv_share(party_other, nB)
	else:
		r_a = nr.recv_share(party_A, nB)
		r_b = nr.recv_share(party_B, nB)

	r = mult(self_pid, socket_list, [(self_pid, r_a), (self_pid, r_b)], t, N, nB)[1]

	# obtain random input s
	if self_pid == B:
		s_val = randint(1,N-1)
		s_shares = ss.gen_shares(n, t, s_val, N)
		ns.distribute_secret(s_shares, socket_list, nB)
		s = s_shares[self_pid-1][1]

	else:
		s = nr.recv_share(party_B, nB)

	u = mult(self_pid, socket_list, ((self_pid, r), (self_pid, r)), t, N, nB)[1]
	u = add(self_pid, socket_list, ((None, d), (None, u)), N)[1]
	u = mult(self_pid, socket_list, ((self_pid, u), (self_pid, s)), t, N, nB)[1]

	# reconstruct t (A) and find jacobi of t and s
	if self_pid == A:
		u_shares_recvd = nr.recv_shares(socket_list, nB)
		u_shares_recvd[A-1] = (A,u)
		f = ss.interpolate_poly(u_shares_recvd, N)
		u_val = f(0)
		j_u_val = jacobi(int(u_val),N)
	
	else:
		nr.send_share([party_A], u, nB)

	if self_pid == B:
		j_s_val = jacobi(int(s_val), N)

	# share jacobi symbols
	if self_pid == A:
		j_u_shares = ss.gen_shares(n, t, j_u_val, N)
		ns.distribute_secret(j_u_shares, socket_list, nB)
		j_u = j_u_shares[self_pid-1][1]
		j_s = nr.recv_share(party_B, nB)

	elif self_pid == B:
		j_s_shares = ss.gen_shares(n, t, j_s_val, N)
		ns.distribute_secret(j_s_shares, socket_list, nB)
		j_s = j_s_shares[self_pid-1][1]
		j_u = nr.recv_share(party_A, nB)

	else:
		j_u = nr.recv_share(party_A, nB)
		j_s = nr.recv_share(party_B, nB)

	# calculate jacobi symbol of d+r^2
	j_fin = mult(self_pid, socket_list, ((self_pid, j_u), (self_pid, j_s)), t, N, nB)[1]
	j_tilde = add(self_pid, socket_list, ((None,j_fin), (None,1)), N)[1]

	fin_share = j_tilde * mmh.find_inv_mod(2, N) % N
	return (self_pid, fin_share)



def test_equality(self_pid, socket_list, comp_shares, t, N, nB, act_parties, iters):
	'''
	test equality repeatedly of two shared secrets to reduce probability of false positives, probabilty of false positives is 1/2^iters
	@arg		: self party id, list of party sockets, tuple of shares to be compared, prime base,
				  share size, pids of contributing parties, number of test_equality_once iterations
	@returns 	: share of equality boolean x==y
	'''
	eq_shares = []
	for x in xrange(iters):
		eq_shares.append(test_equality_once(self_pid, socket_list, comp_shares, t, N, nB, act_parties))

	final_share = rec_mult(self_pid, socket_list, eq_shares, t, N, nB)
	return final_share


'''
 Implementation of Toft's comparison protocol
  @arg		: self party id, list of party sockets, tuple of shares to be compared, prime base,
  		  share size, pids of Alice and Bob, l parameter
  @returns	: secret share of boolean output x > y
'''
def compare(self_pid, socket_list, comp_shares, t, N, nB, act_parties, l):
	x, y = comp_shares
	n = len(socket_list)
	# Check if comparing single bit values. If so, answer is trivial
	if l == 1:
		# `gt' encodes x > y
		xy = mult(self_pid, socket_list, comp_shares, t, N, nB)
		gt = add(self_pid, socket_list, [x, neg(xy, N)], N)
		# `eq' encodes x == y by calculating xy + (1-x)(1-y)
		neg_x = (self_pid, (1 - x[1]) % N)
		neg_y = (self_pid, (1 - y[1]) % N)
		eq = mult(self_pid, socket_list, (neg_x, neg_y), t, N, nB)
		eq = add(self_pid, socket_list, (eq, xy), N)
		# Return gt_eq = gt | eq , calculated as x+y-xy
		gt_eq = mult(self_pid, socket_list, (eq, gt), t, N, nB)
		gt_eq = add(self_pid, socket_list, [gt, eq, gt_eq], N)
		return gt_eq

	# Note here that like equality testing, the roles of the active
	# parties are not the same; the first is Alice, and the second is
	# Bob
	alice, bob = act_parties
	z = add(self_pid, socket_list, [(None,2**l), x, neg(y,N)], N)
	if self_pid == bob:
		# Choose random r
		r = randint(1,N-1)
		# Generate and distribute shares of this random number
		r_sh = ss.gen_shares(n, t, r, N)
		ns.distribute_secret(r_sh, socket_list, nB)
		# Calculate Bob's share of `c' and send it to Alice
		c = add(self_pid, socket_list, [r_sh[self_pid-1], z], N)[1]
		nr.send_share([socket_list[alice-1]], c, nB)
		c = (self_pid, c)
		# Find r_bar, r_bot and r_top and share them
		r_bar = r % (2**l)
		r_bar_sh = ss.gen_shares(n, t, r_bar, N)
		ns.distribute_secret(r_bar_sh, socket_list, nB)

		r_bot = r % (2**(l/2))
		r_bot_sh = ss.gen_shares(n, t, r_bot, N)
		ns.distribute_secret(r_bot_sh, socket_list, nB)

		r_top = floor(r / (2**(l/2))) % 2**(l/2)
		r_top_sh = ss.gen_shares(n, t, r_top, N)
		ns.distribute_secret(r_top_sh, socket_list, nB)

		# Receive shares of c_bar, _bot, _top
		c_bar = (self_pid, nr.recv_share(socket_list[alice-1], nB))
		c_bot = (self_pid, nr.recv_share(socket_list[alice-1], nB))
		c_top = (self_pid, nr.recv_share(socket_list[alice-1], nB))

		# Replace clear values of `r', bar, bot, top with shares
		# This is done for consistency of convention across parties
		r = r_sh[self_pid - 1]
		r_bar = r_bar_sh[self_pid - 1]
		r_bot = r_bot_sh[self_pid - 1]
		r_top = r_top_sh[self_pid - 1]

	elif self_pid == alice:
		# Receive share of `r' from Bob
		r = nr.recv_share(socket_list[bob-1], nB)
		# Calculate own share of `c'
		c_own = add(self_pid, socket_list, [z,(None,r)], N)[1]
		# Reconstruct `c'
		c = nr.reconstruct_secret_recv_only(socket_list, (self_pid, c_own), self_pid, nB, N)
		# Find c_bar, c_bot and c_top and share them
		c_bar = c % (2**l)
		c_bar_sh = ss.gen_shares(n, t, c_bar, N)
		ns.distribute_secret(c_bar_sh, socket_list, nB)

		c_bot = c % (2**(l/2))
		c_bot_sh = ss.gen_shares(n, t, c_bot, N)
		ns.distribute_secret(c_bot_sh, socket_list, nB)

		c_top = floor(c / (2**(l/2))) % 2**(l/2)
		c_top_sh = ss.gen_shares(n, t, c_top, N)
		ns.distribute_secret(c_top_sh, socket_list, nB)

		# Receive shares of r_bar, _bot, _top
		r_bar = (self_pid, nr.recv_share(socket_list[bob-1], nB))
		r_bot = (self_pid, nr.recv_share(socket_list[bob-1], nB))
		r_top = (self_pid, nr.recv_share(socket_list[bob-1], nB))

		# Replace clear values of `c', bar, bot, top with shares
		# This is done for consistency of convention across parties
		c = (self_pid, c_own)
		c_bar = c_bar_sh[self_pid - 1]
		c_bot = c_bot_sh[self_pid - 1]
		c_top = c_top_sh[self_pid - 1]

	else:
		# Receive share of `r' from Bob
		r = nr.recv_share(socket_list[bob-1], nB)
		# Calculate own share of `c' and send to Alice
		c = add(self_pid, socket_list, [z,(None,r)], N)[1]
		nr.send_share([socket_list[alice-1]], c, nB)
		# Receive shares of r_bar, _bot, _top
		r_bar = (self_pid, nr.recv_share(socket_list[bob-1], nB))
		r_bot = (self_pid, nr.recv_share(socket_list[bob-1], nB))
		r_top = (self_pid, nr.recv_share(socket_list[bob-1], nB))
		# Receive shares of c_bar, _bot, _top
		c_bar = (self_pid, nr.recv_share(socket_list[alice-1], nB))
		c_bot = (self_pid, nr.recv_share(socket_list[alice-1], nB))
		c_top = (self_pid, nr.recv_share(socket_list[alice-1], nB))

	# Common steps carried out by all parties

	# Check if r_top = c_top, store in boolean `b'
	b = test_equality(self_pid, socket_list, [r_top, c_top], t, N, nB, act_parties, 10)
	# Compute c_tilde = b ? c_bot:c_top
	c_tilde = add(self_pid, socket_list, [c_bot, neg(c_top, N)], N)
	c_tilde = mult(self_pid, socket_list, [c_tilde, b], t, N, nB)
	c_tilde = add(self_pid, socket_list, [c_tilde, c_top], N)
	# Compute r_tilde = b ? r_bot:r_top
	r_tilde = add(self_pid, socket_list, [r_bot, neg(r_top, N)], N)
	r_tilde = mult(self_pid, socket_list, [r_tilde, b], t, N, nB)
	r_tilde = add(self_pid, socket_list, [r_tilde, r_top], N)

	# Compute u = 1 - (c_tilde>=r_tilde) recursively
	u = (1 - compare(self_pid, socket_list, [c_tilde, r_tilde], t, N, nB, act_parties, l/2)[1]) % N

	# Last few steps, local
	z_bar = add(self_pid, socket_list, [c_bar, neg(r_bar, N), (None, (2**l)*u % N)], N)
	z_l = add(self_pid, socket_list, [z, neg(z_bar, N)], N)
	z_l = (z_l[0], z_l[1] * mmh.find_inv_mod(2**l, N) % N)

	return z_l
