# CSE 310 Programming Assignment #3

## **Overview of the Assignment**
In this assignment, you will gain a better understanding of the Internet Control Message Protocol (ICMP). You will learn to implement a Ping application using ICMP request and reply messages.

### Key Concepts:
- **Ping**: A computer network application used to test whether a particular host is reachable across an IP network. It sends ICMP "echo request" packets to the target host and listens for ICMP "echo reply" replies, sometimes called pongs.
- **ICMP (Internet Control Message Protocol)**: A network layer protocol used by network devices to diagnose network communication issues. ICMP messages are used for operations such as pinging.
- **Round-Trip Time (RTT)**: The time it takes for a signal to go from the sender to the receiver and back. Ping measures the RTT for each packet.
- **Packet Loss**: The failure of one or more transmitted packets to arrive at their destination. Ping records packet loss statistics.

### What the Script Does:
- **Send Ping Requests**: The script sends ping requests to a specified host at approximately one-second intervals. Each message includes a payload with a timestamp.
- **Receive Pong Replies**: After sending each ping request, the script waits up to one second for a reply. If no reply is received within one second, it assumes the packet was lost or the server is down.
- **Calculate Round-Trip Time**: For each received pong reply, the script calculates the RTT and prints it out individually.
- **Record Statistics**: When the program is terminated (via control+c), it prints a statistical summary of the ping session, including the minimum, maximum, and average RTTs.

## **Instructions on running the code:**
1. Open terminal in this directory
2. Run the Python file with the command: <code>python pinger.py [ip address]</code>
    - *Some server ip addresses may block certain types of ICMP packets*
3. Each pong packet will then show up with their respective round-trip time.
    - *User may sometime be prompt with "Request timed out" if a packet is not received*
4. Upon pressing control+c the program will terminate and prompt the user with the statistics of this pinging session or a message for no pong received

**NOTE: For the code to run you need to have Python installed and added to you PATH.<br>**

Installation details regarding Python can be found below:<br>
- https://www.python.org/downloads/
