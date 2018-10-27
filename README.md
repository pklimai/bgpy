# BGPy - BGP in Python

This is an incomplete implementation of BGP (RFC4271) in Python3. 
Use for labbing and stress testing networking equipment at your own risk.
Only control plane is going to be implemented.

Features so far:
- Open connection to specified router host (TCP client socket on port 179)
- Send BGP Open and Keepalive messages so the session comes to Established state
- Send the specified number of IPv4 host prefixes (/32) starting from a given prefix
- Receive and decode messages from peer (Update partially decoded)

TODO:
- Improve attributes decoding in Update messages
- Support other NLRI families (INET-VPN, EVPN)
- Better way of passing parameters
- Unit tests

Example run (session between BGPy script and Juniper vMX):

```
Sent 45 bytes in Open message
Sent 19 bytes in Keepalive message
Sending 2000 routes to the peer...
   ...done!
2018-10-27 13:01:39.867328  Received BGP message:
  Message type: 1 (OPEN)
  Message length:  71
  BGP version: 4
  AS: 65000
  Hold time: 90
  BGP ID: 10.254.0.41
  Optional parameters length: 42
    Optional parameter type 2, len 6, val b'\x01\x04\x00\x01\x00\x01'
      Capability type 1, len 4, val b'\x00\x01\x00\x01'
        Multiprotocol extensions AFI 1, SAFI 1
    Optional parameter type 2, len 6, val b'\x01\x04\x00\x02\x00\x01'
      Capability type 1, len 4, val b'\x00\x02\x00\x01'
        Multiprotocol extensions AFI 2, SAFI 1
    Optional parameter type 2, len 2, val b'\x80\x00'
      Capability type 128, len 0, val b''
    Optional parameter type 2, len 2, val b'\x02\x00'
      Capability type 2, len 0, val b''
    Optional parameter type 2, len 4, val b'@\x02@x'
      Capability type 64, len 2, val b'@x'
    Optional parameter type 2, len 6, val b'A\x04\x00\x00\xfd\xe8'
      Capability type 65, len 4, val b'\x00\x00\xfd\xe8'
    Optional parameter type 2, len 2, val b'G\x00'
      Capability type 71, len 0, val b''
2018-10-27 13:01:40.863955  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:01:42.193624  Received BGP message:
  Message type: 2 (UPDATE)
  Message length:  53
    Attribute: flags 64, typecode 1, value b'\x00'
    Attribute: flags 64, typecode 2, value b'\x02\x01\xfd\xe8'
    Attribute: flags 64, typecode 3, value b'\n\xfe\x00)'
  NLRI in update:
    11.1.0/24
    11.2.0/24
    11.3.0/24
2018-10-27 13:01:42.193624  Received BGP message:
  Message type: 2 (UPDATE)
  Message length:  77
    Attribute: flags 64, typecode 1, value b'\x00'
    Attribute: flags 64, typecode 2, value b'\x02\x01\xfd\xe8'
    Attribute: flags 144, typecode 14, value b'\x00\x02\x01\x10\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\n\xfe\x00)\x00@\x11\x11\x00\x00\x00\x00\x00\x00@""\x00\x00\x00\x00\x00\x00'
2018-10-27 13:02:09.195552  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:02:37.826688  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:03:02.660342  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:03:31.903555  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:03:56.664199  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:04:25.195822  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:04:53.841960  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
2018-10-27 13:04:54.808583  Received BGP message:
  Message type: 2 (UPDATE)
  Message length:  45
    Attribute: flags 64, typecode 1, value b'\x00'
    Attribute: flags 64, typecode 2, value b'\x02\x01\xfd\xe8'
    Attribute: flags 64, typecode 3, value b'\n\xfe\x00)'
  NLRI in update:
    11.4.0/24
2018-10-27 13:05:04.811853  Received BGP message:
  Message type: 2 (UPDATE)
  Message length:  27
  Withdrawn Routes:
    11.4.0/24
2018-10-27 13:05:21.038413  Received BGP message:
  Message type: 4 (KEEPALIVE)
  Message length:  19
Sent 19 bytes in Keepalive message
```

Session and routes on vMX (2000 routes are sent to vMX):

```
lab@vMX-1> show bgp summary    
Groups: 1 Peers: 1 Down peers: 0
Table          Tot Paths  Act Paths Suppressed    History Damp State    Pending
inet.0               
                    2000       2000          0          0          0          0
inet6.0              
                       0          0          0          0          0          0
Peer                     AS      InPkt     OutPkt    OutQ   Flaps Last Up/Dwn State|#Active/Received/Accepted/Damped...
10.254.0.251          65500       2003          0       0       1           3 Establ
  inet.0: 2000/2000/2000/0
  inet6.0: 0/0/0/0
```

The following is configuration on lab vMX device:

```
lab@vMX-1# show protocols bgp 
group EBGP {
    type external;
    multihop;
    export to-EBGP;
    peer-as 65500;
    neighbor 10.254.0.251 {
        family inet {
            unicast;
        }
        family inet6 {
            unicast;
        }
    }
}

lab@vMX-1# show policy-options 
policy-statement to-EBGP {
    term static {
        from protocol static;
        then accept;
    }
}

lab@vMX-1# show routing-options 
rib inet6.0 {
    static {
        route 1111::/64 reject;
        route 2222::/64 reject;
    }
}
static {
    route 11.1.0.0/24 reject;
    route 11.2.0.0/24 reject;
    route 11.3.0.0/24 reject;
}
autonomous-system 65000;
```

Note, multihop is needed in case you are not directly connected to vMX (remember EBGP sets ttl=1 by default).
