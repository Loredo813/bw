from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.link import TCLink
from mininet.cli import CLI
import threading
import time
from plot_rtt import plot_rtt_results
from statsic import calculate_rtt_statistics
import re


class BandwidthDelayTopo(Topo):
    def build(self):
        # Create hosts and servers
        h1 = self.addHost('h1', ip='140.115.154.245/24')  # Host1
        s1 = self.addHost('s1', ip='140.115.154.246/24')  # Server1
        s2 = self.addHost('s2', ip='140.115.154.247/24')  # Server2

        # Create Open vSwitch
        sw1 = self.addSwitch('sw1')  # Switch1

        # Connect hosts and servers to the switch with specific link parameters
        self.addLink(h1, sw1, cls=TCLink, bw=10)
        self.addLink(s1, sw1, cls=TCLink, bw=10)
        self.addLink(s2, sw1, cls=TCLink, bw=10)


def configure_bandwidth(net, option):
    """
    Configure the bandwidth of the switch interface to Host (h1) based on source IP addresses (s1 and s2).
    """
    sw1 = net.get('sw1')
    h1 = net.get('h1')
    s1 = net.get('s1')
    s2 = net.get('s2')
    
    # 確保 sw1-eth1 存在
    interface = 'sw1-eth1'
    
    # 清除先前的配置
    sw1.cmd(f'tc qdisc del dev {interface} root')

    # 設定 HTB 根節點，預設所有未匹配流量走 default 類別
    sw1.cmd(f'tc qdisc add dev {interface} root handle 1: htb default 30')

    # 設定總帶寬
    sw1.cmd(f'tc class add dev {interface} parent 1: classid 1:1 htb rate 10mbit')

    if option == 1:
        print("Configuring bandwidth: 5Mbps from s1 to h1, 5Mbps from s2 to h1.")
        sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:10 htb rate 5mbit ceil 5mbit')
        sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:20 htb rate 5mbit ceil 5mbit')
    elif option == 2:
        print("Configuring bandwidth: 7Mbps from s1 to h1, 3Mbps from s2 to h1.")
        sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:10 htb rate 7mbit ceil 7mbit')
        sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:20 htb rate 3mbit ceil 3mbit')
    elif option == 3:
        print("Configuring bandwidth: 10Mbps shared.")
        sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:30 htb rate 10mbit ceil 10mbit')
    else:
        print("Invalid option. Keeping default bandwidth.")
        return

    # 預設類別 (未匹配流量)
    sw1.cmd(f'tc class add dev {interface} parent 1:1 classid 1:30 htb rate 1mbit ceil 10mbit')

    # 添加基於來源 IP 的過濾條件
    sw1.cmd(f'tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip src 140.115.154.246 flowid 1:10')  # s1 to h1
    sw1.cmd(f'tc filter add dev {interface} protocol ip parent 1:0 prio 1 u32 match ip src 140.115.154.247 flowid 1:20')  # s2 to h1

    # 預設匹配其他流量
    sw1.cmd(f'tc filter add dev {interface} protocol ip parent 1:0 prio 2 u32 match ip src 0.0.0.0/0 flowid 1:30')

    print("Bandwidth configuration applied. Testing ping connectivity...")

    # 測試連線
    result = s1.cmd('ping -c 3 140.115.154.245')
    result2 = s2.cmd('ping -c 3 140.115.154.245')
    print(result)
    print(result2)
