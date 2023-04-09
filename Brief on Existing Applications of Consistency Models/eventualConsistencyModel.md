# Eventual Consistency

Eventual consistency makes sure that data of each node of the database gets consistent eventually. Time taken by the nodes of the database to get consistent may or may not be defined.

Example
|Processes| | | | |
|---|---|---|---|---|
|P1|W1(x,a)| |R1(x,a)| |
|P2| |R2(x,a)|W1(x,a)|R2(x,a)|

P2's first read will issue an update error as the eventual write has not occured on P2's side yet.

## Applications

Distributed Databases where showing data in real time is not important, but the order in which data was posted was different.

### Instagram

Instagram uses distributed databases for storing user data.
Instagram works on principle of eventual consistency. The data generated at one end by an end user is made available to other end user within few seconds.
