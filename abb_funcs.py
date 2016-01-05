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
	print np.array(B_inv[0])
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
	z_self = (self_pid, (x_self[1]*y_self[1])%N) 

	print "z val: ", z_self
	#randomisation step
	h_shares = ss.gen_shares(n, t, z_self[1], N)
	ns.distribute_secret(h_shares, socket_list, nB)
	h_recvd_shares = nr.recv_shares(socket_list, nB)
	h_recvd_shares[self_pid-1] = h_shares[self_pid-1]
	h_recvd_shares_vals = [i[1] for i in h_recvd_shares]

	h_recvd_vals = np.array(h_recvd_shares_vals)
	print h_recvd_shares
	coeff_arr = gen_coeff_arr(n,N)

	print "coeff_arr: ", coeff_arr
	self_mult_share = np.dot(h_recvd_vals, coeff_arr)

	return (self_pid, self_mult_share)

# def abb_compare(self_pid, socket_list, mult_shares, t, N, nB):




