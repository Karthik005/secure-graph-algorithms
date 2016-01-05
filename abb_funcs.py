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

# def signal_done_proc(prev_party,nxt_party, sig):
# 	if prev_party:
# 		recvd = soh.recv_sig(prev_party)
# 		if recvd == sig:
# 			if nxt_party:
# 				soh.send_sig(nxt_party, sig)
# 			return



def add(self_pid, socket_list, addend_shares, N):
	'''
	add shares listed in addend_shares
	@arg		: self party id, list of sockets, list of shares to be added, prime base
	@returns 	: sum of shares
	'''

	num_parties = len(socket_list)
	sum_of_shares = sum([addend_share for addend_share in addend_shares])%N

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
	x_self,y_self = mult_shares
	z_self = (self_pid, (x_self*y_self)%N) 

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

	return (self_pid, self_mult_share)



def test_equality(self_pid, socket_list, comp_shares, t, N, nB, act_parties):
	'''
	test equality of two shared secrets
	@arg		: self party id, list of party sockets, tuple of shares to be compared, prime base,
				  share size, pids of contributing parties
	@returns 	: share of equality boolean
	'''
	n = len(socket_list)
	x,y = comp_shares
	d = x-y

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

	# print r_a, r_b


	r = mult(self_pid, socket_list, (r_a, r_b), t, N, nB)[1]

	# obtain random input s
	if self_pid == B:
		s_val = randint(1,N-1)
		s_shares = ss.gen_shares(n, t, s_val, N)
		ns.distribute_secret(s_shares, socket_list, nB)
		s = s_shares[self_pid-1][1]

	else:
		s = nr.recv_share(party_B, nB)

	u = mult(self_pid, socket_list, (r, r), t, N, nB)[1]
	u = add(self_pid, socket_list, (d, u), N)[1]
	u = mult(self_pid, socket_list, (u, s), t, N, nB)[1]

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
	j_fin = mult(self_pid, socket_list, (j_u, j_s), t, N, nB)[1]
	j_tilde = add(self_pid, socket_list, (j_fin, 1), N)[1]

	fin_share = j_tilde
	return (self_pid, fin_share)

# def abb_compare(self_pid, socket_list, mult_shares, t, N, nB):




