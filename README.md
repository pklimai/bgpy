# bgpy - BGP in Python

Incomplete implementation of BGP (RFC4271) in Python3. Use for labbing and stress testing networking equipment at your own risk.

Features so far:
- Open connection to specified host (TCP client socket on port 179)
- Send BGP Open and Keepalive messages so the session comes to Established state
- Receive and decode messages from peer (not including Update, so far)

TODO:
- Decode Update messages
- Send Updates as specified by the user
- Keep session open by sending keepalives (so far session shuts down after hold time is expired)

Example run:

```
Sent 29 bytes
Sent 19 bytes
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00?\x01'
Message length:  63
Message type: 1 (OPEN)
Received raw, remainder:  b'\x04\xfd\xe8\x00Z\n\x00\x00\x01"\x02\x06\x01\x04\x00\x01\x00\x01\x02\x02\x80\x00\x02\x02\x02\x00\x02\x04@\x02@x\x02\x06A\x04\x00\x00\xfd\xe8\x02\x02G\x00'
Open message: version 4
  AS 65000
  Hold time 90
  BGP ID 10.0.0.1
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x13\x04'
Message length:  19
Message type: 4 (KEEPALIVE)
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00/\x02'
Message length:  47
Message type: 2 (UPDATE)
Received raw, remainder:  b'\x00\x00\x00\x12@\x01\x01\x00@\x02\x04\x02\x01\xfd\xe8@\x03\x04\n\xfe\x00)\x10\x05\x05\x10\x04\x04'
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x13\x04'
Message length:  19
Message type: 4 (KEEPALIVE)
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x13\x04'
Message length:  19
Message type: 4 (KEEPALIVE)
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x13\x04'
Message length:  19
Message type: 4 (KEEPALIVE)
Received raw:  b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x00\x15\x03'
Message length:  21
Message type: 3 (NOTIFICATION)
Received raw, remainder:  b'\x04\x00'
Notification message: code 4, subcode 0
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
