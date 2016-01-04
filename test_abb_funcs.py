#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Karthik
# @Date:   2016-01-04 13:46:33

from abb_funcs import *
import net_recv as nr
import net_share as ns


def test_abb_add(dealer_ip, self_pid, party_ips, t, nB):
	dealer_sock = nr.connect_to_dealer(dealer_ip, self_pid)
	party_conns = nr.connect_to_parties(self_pid, party_ips)
	x_share = 