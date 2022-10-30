
# CSE 310 Programming Assignment #2

## Overview of analysis_pcap_tcp.py

The `analysis_pcap_tcp.py` file is a Python script designed to analyze PCAP files, which are binary files that capture network traffic. PCAP files store packets captured on the network, and these packets can be analyzed to understand various network protocols, including TCP (Transmission Control Protocol).

### Key Concepts:
- **PCAP File**: A file format used to store captured network traffic.
- **TCP (Transmission Control Protocol)**: A core protocol of the Internet Protocol Suite that ensures reliable, ordered, and error-checked delivery of data between applications running on hosts communicating via an IP network.
- **Flow**: In networking, a flow is a sequence of packets sent from a particular source to a particular destination. A TCP flow is identified by a combination of source and destination IP addresses and ports.
- **SYN and FIN Packets**: These are types of TCP packets. A SYN (synchronize) packet is used to initiate a connection, while a FIN (finish) packet is used to terminate a connection.
- **RTT (Round-Trip Time)**: The time it takes for a signal to go from the sender to the receiver and back.
- **Congestion Window**: A TCP state variable that limits the amount of data the sender can send into the network before receiving an acknowledgment (ACK).

### What the Script Does:
1. **Parse the PCAP File**: The script reads the PCAP file and extracts TCP packets.
2. **Identify TCP Flows**: It identifies distinct TCP flows based on the source and destination IP addresses and ports.
3. **Analyze Transactions**: For each flow, it analyzes the first two transactions (sequences of packets exchanged) between the sender and receiver.
4. **Calculate Throughput**: It calculates the throughput, which is the rate at which data is successfully transferred over the network.
5. **Estimate Congestion Window Sizes**: It estimates the size of the TCP congestion window, which controls the amount of data the sender can send before waiting for an ACK.
6. **Detect Retransmissions**: It detects packet retransmissions caused by either triple duplicate ACKs or timeouts.


## **High Level Summary:**
### **Part A**
**(a)** Look through the PCAP file for distinct tcp flows and append it to a list. A flow is considered distinct if there is no other sender and receiver pair already in the list. The length of this list will be the number of distinct flows that are happening. This list will be used throughout the homework as the variable distinct_flows.

**(b)** Look through the PCAP file, only noting down the first two transactions between the sender and receiver of each distinct tcp flow in distinct_flows. The first transactions will be two tuples from sender to receiver and receiver to sender (This is picked based on their port). Same with the second transaction. These 4 tuples will be stored in a list that is returned. These tuples contain source IP address,destination IP address, source port, destination port, TCP sequence number, TCP acknowledgement number and receiver window size.

**(c)** To obtain the throughput for each distinct tcp flow, the code will need the period as well. It loops through the PCAP file and finds the timestamp of the first packet and the last packet of that particular flow. The first packet is the first communication including the 3 way handshake. The last packet is the first FIN flag thus any other packet following the FIN flag will be ignored. While looping through the code also accumulates the length of the tcp to get the total data. Dividing the total data by the period will get you the throughput which is returned back to the main method.

### **PartB**
**(i)** To get the three congestion windows for each distinct tcp flows, the code will first need a RTT. This can easily be obtained by looking at the 3 way handshake‘s start time and end time. The difference of the end time and start time will yield you an RTT to be used for later in the code. Regularly the RTT of a tcp flow will change throughout its lifespan but because we are only interested in the first 3 congestion windows this RTT will work just fine for estimation purpose. Congestion window size for a certain RTT interval can be obtained by counting the occurrence of the sender talking to the receiver from a lower bound timestamp to an upper bound timestamp. The upper bound will always be 1 RTT greater than the lower bound when looping. The counted occurrence will later be appended to a matrix and returned to the main method to be read as the 3 congestion windows size for all distinct tcp flows.

The congestion window size grows exponentially(*doubles*) until it hits the ssthresh and increases linearly(*increments by 1*). The best example would be seen in **Result of Running Code** > **TCP Flow 3** > **Part B** > **i)** where the First 3 Congestion Window Size is [20, 43, 44]. 

**(ii)** For each flow separate the packets by whether the packet is sent by the sender or received by the sender. The two lists will have elements with the property of index(use for ordering later), seq, and ack. List with tuples of packets sent by the sender will be used for sequence numbers mainly. List with tuples of packets received by the sender will be used for acknowledgement numbers mainly. Get the sequence numbers of the packets where the occurrence of the seq is greater than 1 sent by the sender. Append that to a list1. Get the acknowledgement numbers of the packets where the occurrence of the ack is greater than 3 received by the sender. Append that to a list2. Compose list3 with common elements shared between the two lists. Count the times that the first duplicate ACK time is after the retransmitted packet time in list3. Number of times that retransmission was due to triple duplicate ACK should then be the length of list 3 subtracted by the times that the first duplicate ACK time is after the retransmitted packet time in list3, and retransmission due to timeout should be the length of list1 minus retransmission due to triple duplicate ACK

## **Instructions on running the code:**
1. Open terminal in this directory
2. Run the Python file with the command: <code>python analysis_pcap_tcp.py assignment2.pcap</code>
    - *assignment2.pcap can be subsituted with other PCAP files but for this assignment we will be using assignment2.pcap*
    - *assignment2.pcap is not included in the directory because it was not one of the items to submit, you can download this file on Piazza to the the command above*
3. You should then see informations asked of this assignment

**NOTE: For the code to run you need to have Python installed and added to you PATH and also have dpkt library installed.<br>**

Installation details regarding Python and dpkt can be found below:<br>
- https://www.python.org/downloads/
- https://dpkt.readthedocs.io/en/latest/installation.html


## **Result of Running Code:**

```
There are a total of 3 TCP flows:
TCP Flow 1

------
Part A
------
a)
        (source port, source IP address, destination port, destination IP address) = (43498, '130.245.145.12', 80, '128.208.2.198')
b)
        First Transaction : (130.245.145.12 at port 43498) to (128.208.2.198 at port 80)
                Sequence Number = 705669103
                Acknowledgement number = 1921750144
                Receive Window Size = 3

        First Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43498)
                Sequence Number = 1921750144
                Acknowledgement number = 705669127
                Receive Window Size = 3

        Second Transaction : (130.245.145.12 at port 43498) to (128.208.2.198 at port 80)
                Sequence Number = 705669127
                Acknowledgement number = 1921750144
                Receive Window Size = 3

        Second Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43498)
                Sequence Number = 1921750144
                Acknowledgement number = 705670575
                Receive Window Size = 3

c)
        Sender(43498) to Receiver(80) - Throughput: 5342631.414119826 bytes per second

------
Part B
------
i)
        First 3 Congestion Window Size : [14, 18, 41]
ii)
        Retransmission due to triple duplicate ACK: 2
        Retransmission due to timeout: 1


-------------------------------------------------------------------------------------------------------------------------

TCP Flow 2

------
Part A
------
a)
        (source port, source IP address, destination port, destination IP address) = (43500, '130.245.145.12', 80, '128.208.2.198')
b)
        First Transaction : (130.245.145.12 at port 43500) to (128.208.2.198 at port 80)
                Sequence Number = 3636173852
                Acknowledgement number = 2335809728
                Receive Window Size = 3

        First Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43500)
                Sequence Number = 2335809728
                Acknowledgement number = 3636173876
                Receive Window Size = 3

        Second Transaction : (130.245.145.12 at port 43500) to (128.208.2.198 at port 80)
                Sequence Number = 3636173876
                Acknowledgement number = 2335809728
                Receive Window Size = 3

        Second Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43500)
                Sequence Number = 2335809728
                Acknowledgement number = 3636175324
                Receive Window Size = 3

c)
        Sender(43500) to Receiver(80) - Throughput: 1268045.3671424184 bytes per second

------
Part B
------
i)
        First 3 Congestion Window Size : [10, 20, 33]
ii)
        Retransmission due to triple duplicate ACK: 4
        Retransmission due to timeout: 90


-------------------------------------------------------------------------------------------------------------------------

TCP Flow 3

------
Part A
------
a)
        (source port, source IP address, destination port, destination IP address) = (43502, '130.245.145.12', 80, '128.208.2.198')
b)
        First Transaction : (130.245.145.12 at port 43502) to (128.208.2.198 at port 80)
                Sequence Number = 2558634630
                Acknowledgement number = 3429921723
                Receive Window Size = 3

        First Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43502)
                Sequence Number = 3429921723
                Acknowledgement number = 2558634654
                Receive Window Size = 3

        Second Transaction : (130.245.145.12 at port 43502) to (128.208.2.198 at port 80)
                Sequence Number = 2558634654
                Acknowledgement number = 3429921723
                Receive Window Size = 3

        Second Transaction : (128.208.2.198 at port 80) to (130.245.145.12 at port 43502)
                Sequence Number = 3429921723
                Acknowledgement number = 2558636102
                Receive Window Size = 3

c)
        Sender(43502) to Receiver(80) - Throughput: 1626651.9966873797 bytes per second

------
Part B
------
i)
        First 3 Congestion Window Size : [20, 43, 44]
ii)
        Retransmission due to triple duplicate ACK: 0
        Retransmission due to timeout: 0


-------------------------------------------------------------------------------------------------------------------------
```