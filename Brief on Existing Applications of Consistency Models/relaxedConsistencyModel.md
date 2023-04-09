# Consistency Model

## Examples

1. [Kerrighed - Sequential Consistency](./sequentialConsistencyModel.md)

Open source single-system image (SSI) cluster software

2. Open SSI

open-source single-system image clustering system

3. MOSIX

Distributed OS

4. TerraCotta

5. TreadMarks - Lazy Implementation of Release Consistency

(DSM) system for standard Unix systems such as SunOS and Ultrix

6. VODCA - View-based Consistency (Part of Entry Consistency)

High Performance DSM

7. DIPC - Strict Consistency

8. [GFS (Google File System) - Relaxed Consistency](#gfs)

8. [Social Media Platforms - Eventual Consistency](./eventualConsistencyModel.md)

Twitter, Instagram, Facebook Meta, Amazon Shopping

## Application

1. Database Replication

Data centric consistency models guarantee that the results of read and write operations which is performed on data can be replicated to various stores located nearby immediately.

2. Cache Consistency

## Types

### 1. Release Consistency Model

#### Applications

1. Stanford DASH

### 2. Relaxed Consistency Model

#### Applications

1. <span id="gfs">Google File System (GFS)</span>

GFS provides a relaxed consistency model, which works well for Google’s highly distributed application but remains relatively simple and efficient to implement. Here, the authors describe two states of a file region:

1. A file region is consistent if all clients will always see the same data, despite which replica they read from.
2. A file region is defined if after a mutation it is consistent and the clients will see what the mutation writes in its entirety (i.e. the mutation is written without being interleaved by other data from other mutations).

When a non-concurrent mutation succeeds (all replicas report success), the file region is defined and thus, consistent. However, in the event of concurrent successful mutations, the file region is consistent but may not be defined: all clients see the same data but typically it consists of interleaved fragments from multiple mutations.

A failed mutation (at least 1 replica does not report success) indicates that the file region is not consistent and thus, not defined. In such events of failure, the GFS client simply re-runs the mutation.
