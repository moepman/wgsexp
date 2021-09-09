import time
from datetime import datetime, timedelta

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY
from pyroute2 import NDB, WireGuard


class CustomCollector(object):
    @staticmethod
    def collect():
        with NDB() as ndb, WireGuard() as wg:
            wg_interfaces = [
                interface.get("ifname")
                for interface in ndb.interfaces.values()
                if interface.get("kind", "") == "wireguard"
            ]

            gm_peers_configured = GaugeMetricFamily("wireguard_peers_configured", "Number of wireguard peers configured", labels=["interface"])
            gm_peers_connected = GaugeMetricFamily("wireguard_peers_connected", "Number of wireguard peers connected", labels=["interface"])
            gm_peers_alive = GaugeMetricFamily("wireguard_peers_alive", "Number of wireguard peers currently alive", labels=["interface"])

            for wg_interface in wg_interfaces:
                wg_infos = wg.info(wg_interface)
                three_minutes_ago = (datetime.now() - timedelta(minutes=3)).timestamp()

                num_peers = 0
                num_peers_connected = 0
                num_peers_alive = 0
                for wg_info in wg_infos:
                    wg_peers = wg_info.get_attr("WGDEVICE_A_PEERS")
                    num_peers += len(wg_peers)
                    num_peers_connected += len([True for peer in wg_peers if peer.get_attr("WGPEER_A_LAST_HANDSHAKE_TIME").get("tv_sec", int()) > 0])
                    num_peers_alive += len([True for peer in wg_peers if peer.get_attr("WGPEER_A_LAST_HANDSHAKE_TIME").get("tv_sec", int()) > three_minutes_ago])

                gm_peers_configured.add_metric([wg_interface], num_peers)
                gm_peers_connected.add_metric([wg_interface], num_peers_connected)
                gm_peers_alive.add_metric([wg_interface], num_peers_alive)
            yield gm_peers_configured
            yield gm_peers_connected
            yield gm_peers_alive


if __name__ == '__main__':
    REGISTRY.register(CustomCollector())

    start_http_server(8000)

    while True:
        time.sleep(5)
