import random
import struct

from clients.udp_test import UdpTest


class DnsTest(UdpTest):
    def get_default(self):
        return {
            'host': "8.8.8.8",
            'port': 53,
            'timeout': 5,
            'url': 'google.com',
            'dns_rules': {

            }
        }

    @staticmethod
    def _build_packet(url):
        randint = random.randint(0, 65535)
        packet = struct.pack(">H", randint)  # Query Ids (Just 1 for now)
        packet += struct.pack(">H", 0x0100)  # Flags
        packet += struct.pack(">H", 1)  # Questions
        packet += struct.pack(">H", 0)  # Answers
        packet += struct.pack(">H", 0)  # Authorities
        packet += struct.pack(">H", 0)  # Additional
        split_url = url.split(".")
        for part in split_url:
            packet += struct.pack("B", len(part))
            for s in part:
                packet += struct.pack('c', s.encode())
        packet += struct.pack("B", 0)  # End of String
        packet += struct.pack(">H", 1)  # Query Type
        packet += struct.pack(">H", 1)  # Query Class
        return packet

    def _create_message(self):
        return DnsTest._build_packet(self.url)
