import hazelcast
import time

if __name__ == "__main__":
    hz = hazelcast.HazelcastClient( 
        cluster_members=[
        "192.168.111.1:5701",
        "192.168.111.2:5701",
        "192.168.111.3:5701"
    ],
    lifecycle_listeners=[
        lambda state: print("Lifecycle event >>>", state),
    ])
    map = hz.get_map("lab2_map")
    key = "key"
    map.put_if_absent(key, 1)
    for i in range(100):
        map.lock(key).result()
        try:
            value = map.get(key).result()
            time.sleep(0.1)
            value+=1
            map.put(key, value)
        finally:
            map.unlock(key).result()

    print("Finished! Result = ", map.get(key).result())

    hz.shutdown()