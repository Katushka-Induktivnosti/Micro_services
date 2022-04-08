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

queue = hz.get_queue("queue").blocking()

for i in range(25):
    value = queue.take()
    print('Read value is: ', value)
    time.sleep(1)

hz.shutdown()