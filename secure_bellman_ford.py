#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: karthik
# @Date:   2016-01-06 14:40:20


import abb_funcs as abb
import net_recv as nr
import net_share as ns
# import isboolean ; edit this line


# globals
nB = 20
# -------

def update_element(self_pid, socket_list, l, i, x, N):
	'''
	update shared list at shared position with shared value
	@arg		: self party id, list of party sockets, shared list, shared index list, share of val
	@return 	: shared list with element updated
	'''
	for j in xrange(len(l)):
		inter = abb.add(self_pid, socket_list, (x,abb.neg(l[j],N)), N)
		inter = abb.mult(self_pid, socket_list, (inter, i[j]), t, N, nB)
		l[j] = abb.add(self_pid, socket_list,(inter, l[j]) , N)

	return l


def secure_bellman_ford(self_pid, socket_list, G, src_v_ind, init_party_id, N, t = 1):
	'''
	find shortest paths to all vertices from source vertex, find predecessors along path
	@arg		: self party id, list of party sockets, shared graph, initializer party to distribute shares of 0 and T
				  share of source vertex id, share of val
	@return 	: shared predecessors, shared shortest paths
	'''
	V_num = len(G[0])
	p = []
	d = []
	init_party = socket_list[init_party_id-1]
	# initialization
	if self_pid == init_party_id:
		T = 256 
		for i in xrange(V_num):
			zero_shares = ss.gen_shares(n, t, 0, N)
			ns.distribute_secret(zero_shares, socket_list, nB)
			p.append(zero_shares[self_pid-1])
			T_shares = ss.gen_shares(n, t, T, N)
			ns.distribute_secret(zero_shares, socket_list, nB)
			d.append(T_shares[self_pid-1])
	else:
		for i in xrange(V_num):
			zero_sh = nr.recv_share(init_party, nB)
			p.append((self_pid,zero_sh))
			T_sh = nr.recv_share(init_party, nB)
			d.append((self_pid,zero_sh))

	if self_pid == init_party_id:
		zero_shares = ss.gen_shares(n, t, 0, N)
		ns.distribute_secret(zero_shares, socket_list, nB)
		zero = zero_shares[self_pid-1]
		one_shares = ss.gen_shares(n, t, 1, N)
		ns.distribute_secret(one_shares, socket_list, nB)
		one = zero_shares[self_pid-1]
		threshold_shares = ss.gen_shares(n, t, 256, N)
		ns.distribute_secret(threshold_shares, socket_list, nB)
		threshold =threshold_shares[self_pid-1]
	else:
		zero_sh = nr.recv_share(init_party, nB)
		zero = (self_pid,zero_sh)
		one_sh = nr.recv_share(init_party, nB)
		one = (self_pid,zero_sh)
		threshold_sh = nr.recv_share(init_party, nB)
		threshold = (self_pid,threshold_sh)

	# update distance of source vertex to 0
	d = update_element(self_pid, socket_list, d, src_v_ind, zero, N)


	error_vec = []

	# iterative updates to distances and predecessors
	for i in xrange(V_num):
		for j in xrange(V_num):
			for k in xrange(V_num):
				y = abb.add(self_pid, socket_list, [d[k], neg(d[j], N)], N)
				y = abb.add(self_pid, socket_list, [y, G[j][k]], N)
				y = y+256
				x = abb.inequality(self_pid, party_conns, (threshold, y), t, N, nB, (1,2), 4)
				error_vec.append(abb.is_boolean(self_pid, socket_list, x, t, N, nB, (1,2)))
				x_y = abb.mult(self_pid, socket_list, (y,x), t, N, nB)
				
				d[j] = abb.add(self_pid, socket_list, [d[j], x_y], N)
				prod_1 = abb.add(self_pid, socket_list, [one, neg(x, N)], N)
				prod_1 = abb.mult(self_pid, socket_list, (prod_1,p[j]), t, N, nB)
				prod_2 = (x*k)%N
				p[j] = abb.add(self_pid, socket_list, [prod_1, prod_2], N)

	error_bool_sh = abb.rec_mult(self_pid, socket_list, error_vec, t, N, nB)

	return p, d, error_bool_sh


def reconstruct_preds_dists(self_pid, socket_list, p, d, error_bool_sh, N):
	'''
	reconstruct predecessors, distances and error boolean
	'''
	p_vals = []
	d_vals = []
	for i in range(len(p)):
		p_vals.append(nr.reconstruct_secret(socket_list, p_vals[i], self_pid, nB, N))
		d_vals.append(nr.reconstruct_secret())

	error_bool = nr.reconstruct_secret(socket_list, error_bool_sh, self_pid, nB, N)
	return p_vals, d_vals, error_bool


def sec_bf_wrapper(self_pid, socket_list, G, src_v_ind, init_party_id, N):
	'''
	secure bellman ford wrapper function
	'''
	p, d, error_bool_sh = secure_bellman_ford(self_pid, socket_list, G, src_v_ind, init_party_id, N)
	p_vals, d_vals, error_bool = reconstruct_preds_dists(self_pid, socket_list, p, d, error_bool_sh, N)
	print p_vals, d_vals, error_bool
	if not error_bool:
		raise ValueError('encountered errors in abb operations; output may be incorrect')

	return p_vals, d_vals, error_bool
