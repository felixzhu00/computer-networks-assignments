import dpkt as dp
import socket
import sys


def get_flows(filename):
    # The specific distinct flow pairs in the PCAP file(identified by their unique 4-tuple)
    distinct_flows = []
    for ts, raw in dp.pcap.Reader(open(filename, "rb")):
        eth = dp.ethernet.Ethernet(raw)
        ip = eth.data
        tcp = ip.data
        sip = socket.inet_ntoa(ip.src)                  # source IP
        dip = socket.inet_ntoa(ip.dst)                  # destination IP
        sport = tcp.sport                               # source port
        dport = tcp.dport                               # destination port
        # Check for SYN flag and add the unique flow pairs to distinc_flows
        if (tcp.flags & dp.tcp.TH_SYN):
            duplicate_flag = False                      #Makes sure that no duplicate get into the list
            for flow in distinct_flows:
                if (flow[0] == sport and flow[2] == dport) or (flow[0] == dport and flow[2] == sport):
                    duplicate_flag = True
                    break
            if not duplicate_flag:
                distinct_flows.append((sport, sip, dport, dip))
    return distinct_flows

def get_first_two(filename, distinct_flows):
    result = [[] for _ in range(len(distinct_flows)*2)]
    counter = [0 for _ in range(len(distinct_flows))]
    for ts, raw in dp.pcap.Reader(open(filename, "rb")):
        eth = dp.ethernet.Ethernet(raw)
        ip = eth.data
        tcp = ip.data
        sip = socket.inet_ntoa(ip.src)                      #source IP
        dip = socket.inet_ntoa(ip.dst)                      #destination IP
        sport = tcp.sport                                   #source port
        dport = tcp.dport                                   #destination port
        for i, flow in enumerate(distinct_flows):
            #Skips the 3 way handshake
            if ((flow[0] == sport and flow[2] == dport) or (flow[0] == dport and flow[2] == sport)) and counter[i] < 3:
                counter[i] += 1
            else:
                if flow[0] == sport and flow[2] == dport:
                    if len(result[2*i]) == 0 or len(result[2*i]) == 1:
                        result[2*i].append((sip, dip, sport,dport, tcp.seq, tcp.ack, tcp.win))          #append to even index, later be print as sender to receiver
                elif flow[0] == dport and flow[2] == sport:
                    if len(result[2*i + 1]) == 0 or len(result[2*i + 1]) == 1:
                        result[2*i+1].append((sip, dip, sport,dport, tcp.seq, tcp.ack, tcp.win))        #append to odd index, later be print as receiver to sender
    return result

def get_throughput(filename, distinct_flows):
    total_data = [0 for _ in range(len(distinct_flows))]    #array that contains the cumulative data of each flow
    first = [None for _ in range(len(distinct_flows))]      #array of first timestamp for each flow. Including the 3 way handshake
    last = [None for _ in range(len(distinct_flows))]       #array of last timestamp for each flow. Excluding everything after the first FIN flag

    for ts, raw in dp.pcap.Reader(open(filename, "rb")):
        eth = dp.ethernet.Ethernet(raw)
        ip = eth.data
        tcp = ip.data
        sport = tcp.sport
        dport = tcp.dport
        for i, flow in enumerate(distinct_flows):
            if flow[0] == sport and flow[2] == dport:
                total_data[i] += len(tcp)                   #add length of each data to total data
                if first[i] == None:
                    first[i] = ts                           #set first timestamp
                if tcp.flags & dp.tcp.TH_FIN:
                    last[i] = ts                            #set last timestamp

    throughputs = []

    for i, data in enumerate(total_data):
        period = last[i] - first[i]                         #calculate period (Difference in the first and last)
        throughputs.append((data / period))                 #throughput = total data over that period

    return throughputs

def get_congestion_window(filename, distinct_flows):
    packets = [[] for _ in range(len(distinct_flows))]      #array of array storing the packets to be pass to another method, contains tuple (timestamp, TCP)
    counter = [0 for _ in range(len(distinct_flows))]       #counter to skip 3 way handshake for each flow
    handshake_ts = [[] for _ in range(len(distinct_flows))] #the timestamp for 3 way handshake of each flow, use to calculate the RTT later down the line 

    cwnds = []                                              #returned result
    for ts, raw in dp.pcap.Reader(open(filename, "rb")):
        eth = dp.ethernet.Ethernet(raw)
        ip = eth.data
        tcp = ip.data
        sport = tcp.sport
        dport = tcp.dport
        for i, flow in enumerate(distinct_flows):
            if ((flow[0] == sport and flow[2] == dport) or (flow[0] == dport and flow[2] == sport)) and counter[i] < 3:
                handshake_ts[i].append(ts)                  #append handshake timestamp
                counter[i] += 1
            if (flow[0] == sport and flow[2] == dport) or (flow[0] == dport and flow[2] == sport):
                packets[i].append((ts, tcp))                #append (timestamp, TCP)
    for i, flow in enumerate(distinct_flows):
        handshake_rtt = handshake_ts[i][2] - handshake_ts[i][0] #using handshake RTT as the main RTT to get 3 congestion windows size
        cwnds.append(get_first_three_cwind(i, handshake_rtt, packets,flow[0],flow[2]))
    return cwnds

def get_first_three_cwind(num, rtt, flows, sport, dport):
    ts_lower_bound = flows[num][3][0]                       #timestamp of TCP after 3 way handshake
    ts_upper_bound = flows[num][3][0] + rtt                 #lowerbound + RTT
    ceiling = flows[num][len(flows[num]) - 1][0]            #the maximum timestamp
    cwnd = []
    for i in range(0, 3):
        counter = 0                                         #counts the number of packets sender send to receiver, use as congestion window size
        if ts_upper_bound <= ceiling:
            for pkt in flows[num]:
                if ts_lower_bound <= pkt[0] < ts_upper_bound:
                    if pkt[1].sport == sport and pkt[1].dport == dport:
                        counter = counter + 1
            cwnd.append(counter)
            ts_lower_bound = ts_upper_bound                 #set lower to upper
            ts_upper_bound = ts_upper_bound + rtt           #new upper is next RTT interval
        elif ts_upper_bound > ceiling:
            for pkt in flows[num]:
                if ts_lower_bound <= pkt[0] <= ceiling:
                    if pkt[1].sport == sport and pkt[1].dport == dport:
                        counter = counter + 1
            cwnd.append(counter)                            #append to cwnd to be passed back
            break
        else:
            break
    return cwnd

def retransmission_helper(sender_to_receiver, receiver_to_sender):
    sender_to_receiver_seq = [packet[1] for packet in sender_to_receiver]                                               #specificly the SEQ number of the packet from sender to receiver
    sender_to_receiver_seq_dictionary = {item:sender_to_receiver_seq.count(item) for item in sender_to_receiver_seq}    #turn sender_to_receiver_seq into a dictionary that counts the freqency of SEQ number

    receiver_to_sender_ack = [packet[2] for packet in receiver_to_sender]                                               #specificly the ACK number of the packet from receiver to sender
    receiver_to_sender_ack_dictionary = {item:receiver_to_sender_ack.count(item) for item in receiver_to_sender_ack}    #turn receiver_to_sender_ack into a dictionary that counts the freqency of ACK number

    duplicate = []                                                                                                      #filter sender_to_receiver_seq_dictionary for only SEQ with counts greater than 1
    for seq, count in sender_to_receiver_seq_dictionary.items():
        if count > 1: 
            duplicate.append(seq)

    triple = []                                                                                                         #filter receiver_to_sender_ack_dictionary for only ACK with counts greater than 3
    for ack, count in receiver_to_sender_ack_dictionary.items():
        if count > 3: 
            triple.append(ack)

    common = [element for element in triple if element in duplicate]                                                    #an array of all common numbers

    counter = 0                                                                                                         

    for e in common:
        first = 0
        send_count = 0
        rec_count = 0
        
        for pkt in receiver_to_sender:
            if pkt[2] == e:                                                                                             #check if ACK match
                rec_count += 1
            if rec_count == 2:                                                                                          #If there is a second same ACK record time(index)
                first = pkt[0]
                break

        for pkt in sender_to_receiver:
            if pkt[1] == e:                                                                                             #check if SEQ match
                send_count += 1
            if send_count == 2:                 
                if first > pkt[0]:                                                                                      #instance of first duplicate ACK time comming after the retransmitted packet time
                    counter += 1
                break
        
    triple_dup = len(common) - counter
    timeout = len(duplicate) - triple_dup
    return triple_dup, timeout

def get_retransmission(filename, distinct_flows):
    result = []
    packets = []
     
    for ts, raw in dp.pcap.Reader(open(filename, "rb")):
        eth = dp.ethernet.Ethernet(raw)
        ip = eth.data
        tcp = ip.data
        packets.append(tcp)
    for flow in distinct_flows:
        sender_to_receiver = []                                                                                         #pass into helper method later
        receiver_to_sender = []                                                                                         #pass into helper method later
        
        index = 0                                                                                                       #use for ordering the different packets between sender and receiver
        
        counter = 0                                                                                                     #skip 3 way handshake packets
        for pkt in packets:
            if ((flow[0] == pkt.sport and flow[2] == pkt.dport) or (flow[2] == pkt.sport and flow[0] == pkt.dport)) and counter < 3:
                counter += 1
                continue
            if flow[0] == pkt.sport and flow[2] == pkt.dport:
                sender_to_receiver.append((index, pkt.seq, pkt.ack))                                                    #if sender to receiver
                index += 1
            elif flow[0] == pkt.dport and flow[2] == pkt.sport:
                receiver_to_sender.append((index, pkt.seq, pkt.ack))                                                    #if receiver to sender
                index += 1
        result.append(retransmission_helper(sender_to_receiver, receiver_to_sender))                                    #pass result to main
    return result


if __name__ == "__main__":
    filename = sys.argv[1]
    flows = get_flows(filename)
    first_two_transactions = get_first_two(filename, flows)
    throughputs = get_throughput(filename, flows)
    cwnds = get_congestion_window(filename, flows)
    retransmissions = get_retransmission(filename, flows)

    print(f"There are a total of {len(flows)} TCP flows:")
    for i, flow in enumerate(flows):
        print(f"TCP Flow {i+1}")
        print("\n------")
        print("Part A")
        print("------")
        print("a) ")
        print(f"\t(source port, source IP address, destination port, destination IP address) = {flow}")
        print("b) ")
        for j in range(2):
            first = first_two_transactions[(2*(i))][j]                  #sender to receiver
            second = first_two_transactions[(2*(i)+1)][j]               #receiver to sender
            placement = "First" if j == 0 else "Second"
            print(f"\t{placement} Transaction : ({first[0]} at port {first[2]}) to ({first[1]} at port {first[3]})")
            print(f"\t\tSequence Number = {first[4]}\n\t\tAcknowledgement number = {first[5]}\n\t\tReceive Window Size = {first[6]}\n")
            print(f"\t{placement} Transaction : ({second[0]} at port {second[2]}) to ({second[1]} at port {second[3]})")
            print(f"\t\tSequence Number = {second[4]}\n\t\tAcknowledgement number = {second[5]}\n\t\tReceive Window Size = {second[6]}\n")
        print("c) ")
        print(f"\tSender({flows[i][0]}) to Receiver({flows[i][2]}) - Throughput: {throughputs[i]} bytes per second")
        print("\n------")
        print("Part B")
        print("------")
        print("i) ")
        print(f"\tFirst 3 Congestion Window Size : {cwnds[i]}")
        print("ii) ")
        print(f"\tRetransmission due to triple duplicate ACK: {retransmissions[i][0]}")
        print(f"\tRetransmission due to timeout: {retransmissions[i][1]}")
        print("\n\n-------------------------------------------------------------------------------------------------------------------------\n")

        
