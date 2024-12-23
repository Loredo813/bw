from mininet.net import Mininet
from mininet.node import OVSSwitch, Controller
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time
import re

# 引入自定義拓撲和配置函數
from main import BandwidthDelayTopo, configure_bandwidth

def run_bandwidth_test(option):
    """
    Run bandwidth tests for s1 and s2 to h1 based on the selected configuration option.
    """
    setLogLevel('info')
    
    # 初始化網路
    topo = BandwidthDelayTopo()
    net = Mininet(topo=topo, switch=OVSSwitch, controller=Controller, link=TCLink, autoSetMacs=True)
    net.start()
    
    try:
        # 設定頻寬
        configure_bandwidth(net, option)
        time.sleep(2)  # 等待頻寬配置生效
        
        s1 = net.get('s1')
        s2 = net.get('s2')
        h1 = net.get('h1')
        
        print("\n--- Starting Bandwidth Test ---")
        # 啟動 iperf 伺服器在 h1 上
        h1.cmd('iperf -s -u -D')  # -D 表示在背景運行
        
        time.sleep(1)  # 確保伺服器啟動
        
        # s1 發送流量到 h1
        print("Testing bandwidth from s1 to h1...")
        result_s1 = s1.cmd('iperf -c 140.115.154.245 -u -b 10M -t 10')
        print(result_s1)
        
        # s2 發送流量到 h1
        print("Testing bandwidth from s2 to h1...")
        result_s2 = s2.cmd('iperf -c 140.115.154.245 -u -b 10M -t 10')
        print(result_s2)
        
        # 提取結果
        s1_bandwidth = extract_bandwidth(result_s1)
        s2_bandwidth = extract_bandwidth(result_s2)
        
        print(f"\n✅ Test Results:")
        print(f"s1 to h1 bandwidth: {s1_bandwidth} Mbps")
        print(f"s2 to h1 bandwidth: {s2_bandwidth} Mbps")
        
    finally:
        net.stop()

def extract_bandwidth(iperf_output):
    """
    Extract bandwidth value from iperf output.
    """
    match = re.search(r'([\d.]+)\s+Mbits/sec', iperf_output)
    if match:
        return float(match.group(1))
    return 0.0

if __name__ == '__main__':
    print("\n--- Testing Option 1: 5Mbps for s1 and 5Mbps for s2 ---")
    run_bandwidth_test(option=1)
    
    print("\n--- Testing Option 2: 7Mbps for s1 and 3Mbps for s2 ---")
    run_bandwidth_test(option=2)
    
    print("\n--- Testing Option 3: Shared 10Mbps ---")
    run_bandwidth_test(option=3)
