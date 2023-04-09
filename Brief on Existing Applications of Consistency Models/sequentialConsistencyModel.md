# Sequential Consistency

The result of any execution is the same as if the operations of all the processors were executed in some sequential order, and the operations of each individual processor appear in this sequence in the order specified by its program

Example

| Site 1 | \_ | \_ | \_ | \_ | \_ | \_ |
|---|---|---|---|---|---|---|
|P1|W(x,a)| | | | | |
|P2| |W(x,b)| | | | |
|P3| | |R(x,b)| |R(x,a)| |
|P4| | | |R(x, b)|R(x,a)| |

| Site 2 | \_ | \_ | \_ | \_ | \_ | \_ |
|---|---|---|---|---|---|---|
|P1|W(x,a)| | | | | |
|P2| |W(x,b)| | | | |
|P3| | |R(x,b)|R(x,a)| |
|P4| | | |R(x,a)|R(x,b)| |

Program order should be preserved which is not happening at site 2.

## Applications

### Kerrighed - (Distributed Shared Memory)

Shared Memory is said to be sequential consistent if all processes see the same order of all memory access operations o the shared memory.

Kerrighed is an extension to Linux Operating System. It is a kernel patch or set of kernel modules. It transfers processes and threads between nodes to balance their workload.

It provides applications like OpenMP, MPI, POSIX models and numerical simulations to use more distributed resources.

Kerrighed keeps local and global resources separately.
It implements the set of global resource management services which manage resource sharing and distribution between applications and provides benefit of using all cluster resources.

A Kerrighed Node can access its available local resources by starting a root container. But it has to start Kerrighed container and add other nodes in Kerrighed container to access the global resources.

Kerrighed provides Distributed Shared Memory with Sequential Consistency. It offers every node a share of the DSM and every node has its own private limited memory

Sequential Consistency is used in Distributed Transactions as well.
