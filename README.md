# BGPy - BGP in Python

This is an incomplete implementation of BGP (RFC4271) in Python3. 
Use for labbing and stress testing networking equipment at your own risk.
Only control plane is going to be implemented.

Features so far:
- Open connection to specified host (TCP client socket on port 179)
- Send BGP Open and Keepalive messages so the session comes to Established state
- Receive and decode messages from peer (Update partially decoded, so far)

TODO:
- Decode attributes and withdrawn routes in Update messages
- Send Updates as specified by the user
- Support different NLRI families
- Better way of passing parameters
- Unit tests

Example run:

```
Sent 29 bytes in Open message
Sent 19 bytes in Keepalive message
2018-10-04 00:13:42.161689  Received BGP message:
  Message length:  63
  Message type: 1 (OPEN)
Open message: version 4
  AS 65000
  Hold time 90
  BGP ID 10.0.0.1
2018-10-04 00:13:42.368215  Received BGP message:
  Message length:  19
  Message type: 4 (KEEPALIVE)
Sent 19 bytes in Keepalive message
2018-10-04 00:13:42.368215  Received BGP message:
  Message length:  48
  Message type: 2 (UPDATE)
  NLRI in update:
    5.5/16
    4.4/16
    /0
2018-10-04 00:14:08.026474  Received BGP message:
  Message length:  19
  Message type: 4 (KEEPALIVE)
Sent 19 bytes in Keepalive message
2018-10-04 00:14:33.199170  Received BGP message:
  Message length:  19
  Message type: 4 (KEEPALIVE)
Sent 19 bytes in Keepalive message
```

The following is configuration on lab vMX device that was used during the exercise:

```
[edit]
lab@vMX-1# show protocols bgp 
group ebgp {
    multihop;
    export to-ebgp;
    peer-as 65500;
    neighbor 10.254.0.251 {
        passive;
    }
}
```

Here, multihop is needed in case you are not directly connected to vMX (remember EBGP sets ttl=1 by default).
