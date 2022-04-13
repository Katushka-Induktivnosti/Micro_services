import hazelcast

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
    map = hz.get_map("lab2-distributed-map").blocking()
    for i in range(1000):
        map.set(i, "value")
    hz.shutdown()
