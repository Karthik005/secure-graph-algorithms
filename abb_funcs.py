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
	vandermonde = np.array([[j**i for j in range(1,n+1)] for i in range(1,n+1)])
	return vandermonde

def gen_reduction_array(n, t):
	'''
	generates reduction array
	@arg		: number of parties, number of corrupted parites (max)
	@returns 	: degree reduction array
	'''
	trunc_arr = np.concatenate(np.ones(t),np.zeros(n-t))
	B = gen_vandermonde(n)
	B_inv = np.linalg.inv(B)
	red_arr = np.dot(np.dot(B,trunc_arr),B_inv)
	return red_arr

def mult(self_pid, socket_list, mult_shares, t, N, nB):
	'''
	multiply shares listed in mult_shares
	@arg		: self party id, list of party sockets, tuple of shares to be multiplied, prime base, share size
	@returns 	: product share
	'''
	n = len(socket_list)

	# generate self share
	x_self,y_self = mult_shares
	z_self = (self_pid, x_self[1]*y_self[1]) 

	#randomisation step
	g_shares = ss.gen_shares(n, t, 0, N)
	ns.distribute_secret(g_shares, socket_list, nB)
	g_recvd_shares = nr.recv_shares(socket_list, nB)
	g_recvd_shares[self_pid-1] = g_shares[self_pid-1]
	g_sum = sum([g_share[1] for g_share in g_shares])%N
	z_tilde = z_self[1]+g_sum

	# degree reduction step
	red_arr = gen_reduction_array(n, t)
	self_mult_share = z_tilde*red_arr[self_pid-1]

	return (self_pid, self_mult_share)

# def abb_compare(self_pid, socket_list, mult_shares, t, N, nB):




