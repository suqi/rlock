# rlock
A distributed resource lock based on redis setnx

## Python实现的分布式互斥锁

基于redis的原子操作setnx，支持超时自动释放，非阻塞（最多尝试次数），自定义等锁时间。
如果锁不存在则直接上锁，否则等待，并判断锁是否已超时，避免进程上锁后挂掉，造成死锁。
应用场景：并行的分布式的不同进程抢夺相同的资源，比如同时去读写一个文件或数据库配置，等等。

爱偷懒的Python同学可以更进一步地在此基础上封装成decorator和with statement。
设计思想参考：http://redis.io/commands/setnx
欢迎大家拍砖。 

—-UPDATE 2014.04.24
Redis的2.6.12版本以上支持了EX,NX参数，可以完美替代setnx，并且实现锁更简单（SET resource-name anystring NX EX max-lock-time），大家可以参考http://redis.io/commands/set

## 应用场景
并行的进程抢夺相同的资源，比如同时去读写一个文件或数据库配置，等等。
Python的Lock主要用于单进程内的多线程的同步， 而这个锁还可以覆盖多个不同的分布式的进程的同步
