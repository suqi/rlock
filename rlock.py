# -*- coding: utf-8 -*-
'''不同的任务间可能会抢夺相同的资源，可以通过互斥锁来同步'''
import redis
import time
import random


PREFIX_LOCK = "LOCK_"
VALUE_DELETED = -1

def acquire_lock(lock_key, timeout=100, max_tries=100, interval=10):
    """
    获取互斥锁后，可以对互斥的资源进行操作
    - 超时自动释放：防止获取锁后进程挂掉，造成死锁 （默认10秒超时）
    - 最多尝试次数：默认10次， 防止尝试太多次数造成死循环
    - 尝试失败等待时间： 默认10秒
    返回： 锁的失效时间
    """
    mutex = PREFIX_LOCK + str(lock_key)
    
    for tries in xrange(1, max_tries+1):
        # 1. try to get lock
        to_expire = time.time() + timeout
        available = get_redis().setnx(mutex, to_expire)
        if available:
            print u"[%s]直接取得锁" % bpm_context.task_id
            return to_expire # acquire smoothly
        else:
            # 2. get lock expire time
            expire_1 = get_redis().get(mutex)
            if not expire_1:
                print u"[%s]先查到有锁，现在突然又被删除了" % bpm_context.task_id
                continue 
            expire_1 = float(expire_1)
            if expire_1 == VALUE_DELETED:
                print u"[%s]锁被删除了，重新再取一次" % bpm_context.task_id
                get_redis().delete(mutex) #再删一遍以防死循环
                continue
            elif expire_1 <= time.time():
                # 3. if expired, refresh the lock
                to_expire = time.time() + timeout
                expire_2 = get_redis().getset(mutex, to_expire)
                if expire_1 == expire_2:
                    print u"[%s]超时了，强制拿锁" % bpm_context.task_id
                    bpm_logger.info("[{}] acquired by forcely refresh timeout({}s)".format(mutex, timeout))
                    return to_expire
                else:
                    print u"[%s]别人抢到了，重新来" % bpm_context.task_id
                    # some other task has acquired lock more quickly, have to retry from step 1
                    continue 
            else:
                # if lock is not expired, have to wait. 
                # sleep randomly to avoid same-time-wake-up of diffrent tasks
                print u"[%s]锁被占了，等一会儿" % bpm_context.task_id
                wait_sec = random.uniform(1, interval)
                print "[{}] wait lock {}s (#{} try failed)".format(mutex, int(wait_sec), tries)
                sleep(wait_sec) 
    return 0


def release_lock(lock_key, expected_expire):
    """
    释放互斥锁
    需要传入该锁的原预设超时时间，来判断是否已经有其他进程强制获取了锁，此时就不应该删除这个锁
    """
    mutex = PREFIX_LOCK + str(lock_key)
    latest_expire = get_redis().get(mutex)
    if expected_expire and latest_expire and expected_expire == float(latest_expire):
		get_redis().delete(mutex)
		print u"[%s]已删除锁" % bpm_context.task_id
	else:
		print u"[%s]发现值已变动，不删除" % bpm_context.task_id
 
        
def get_redis():
    return redis.StrictRedis(**REDIS_CONF)
