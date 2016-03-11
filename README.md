SECURE GRAPH ALGORITHMS
=======================
This is the working repository for the implementation of the secure graph
protocols described in
[ACMPV13](http://link.springer.com/chapter/10.1007/978-3-642-39884-1_21).

The implementation is done in Python.

Authors
=======
* Karthik S
* Yashvanth K

Instructions for Execution
==========================
Usage is currently not straightforward, we hope to change this by writing a
script to automate the following tasks:
* Sharing the graph
* Running an instance of the secure Bellman Ford's algorithm on each system

Currently:
* net_share.py shares a graph from a file
* secure_bellman_ford.py, when run on a separate machine, will automatically
establish connections with the dealer and the other machines
* Each instance of execution of the above program must be supplied the Party ID
by command-line, and executed in order of Party ID
