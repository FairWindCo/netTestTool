import re
import subprocess
import sys


class SystemPing:
    def __init__(self, host: str, count: int = 4, packet_size: int = 56, interval: int = 1000) -> None:
        super().__init__()
        self.host = host
        self.count = count or 4
        self.packet_size = packet_size or 56
        self.interval = interval or 1
        self._std_out = None
        self.result = None
        self.ping_command = 'ping'

    def analise_std_out(self) -> dict:
        return {}

    def run(self):
        result = subprocess.run(self.ping_command, stdout=subprocess.PIPE)
        if result.returncode == 0 or result.returncode == 1:
            self._std_out = list(map(str.strip, filter(lambda s: s.strip(), result.stdout.decode().split('\r'))))
            self.result = self.analise_std_out()
        self.result['is_error'] = result.returncode != 0
        return self.result


class SystemWinPing(SystemPing):
    def __init__(self, host: str, count: int = 4, packet_size: int = 56, interval: int = 1000) -> None:
        super().__init__(host, count, packet_size, interval)
        self.ping_command = f'ping {host} -n {count} -l {packet_size} -w {interval}'
        self.regexp_parent = re.compile(r"^Ping statistics for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}):")
        self.regexp_lost = re.compile(r"^Packets: Sent = (\d+), Received = (\d+), Lost = (\d+) \((\d+)% loss\),")
        self.regexp_time = re.compile(r"^Minimum = (\d+)ms, Maximum = (\d+)ms, Average = (\d+)ms")

    def analise_std_out(self) -> {}:
        length = len(self._std_out)
        index = 0
        result = {
            'peer': self.host,
            'packet_lost': 0,
        }
        while index < length:
            match_peer = self.regexp_parent.match(self._std_out[index])
            if match_peer:
                result['peer'] = match_peer.group(1)
                index += 1
                match_loss = self.regexp_lost.match(self._std_out[index])
                if match_loss:
                    result['packet_lost'] = int(match_loss.group(3))
                    result['lost'] = int(match_loss.group(4))
                    result['send'] = int(match_loss.group(1))
                    result['recv'] = int(match_loss.group(2))
                    index += 1
                    if result['lost'] < 100:
                        index += 1
                        match_timing = self.regexp_time.match(self._std_out[index])
                        if match_timing:
                            result['minimum_time'] = int(match_timing.group(1))
                            result['maximum_time'] = int(match_timing.group(2))
                            result['avg_time'] = int(match_timing.group(3))
                            break
                    else:
                        break
            index += 1
        return result


class SystemLinuxPing(SystemPing):
    def __init__(self, host: str, count: int = 4, packet_size: int = 56, interval: int = 1000) -> None:
        super().__init__(host, count, packet_size, interval)
        self.ping_command = f'ping {host} -c {count} -i {interval} -s {packet_size}'
        self.regexp_parent = re.compile(r"^--- (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) ping statistics ---")
        self.regexp_lost = re.compile(r"^(\d+) packets transmitted, (\d+) received, ([+-]?\d*\.?\d*)% packet loss, time (\d+)ms")
        self.regexp_time = re.compile(r"^rtt min/avg/max/mdev = ([+-]?\d*\.?\d*)/([+-]?\d*\.?\d*)/([+-]?\d*\.?\d*)/([+-]?\d*\.?\d*) ms")

    def analise_std_out(self) -> dict:
        length = len(self._std_out)
        index = 0
        result = {
            'peer': self.host,
            'packet_lost': 0,
        }
        while index < length:
            match_peer = self.regexp_parent.match(self._std_out[index])
            if match_peer:
                result['peer'] = match_peer.group(1)
                index += 1
                match_loss = self.regexp_lost.match(self._std_out[index])
                if match_loss:
                    result['lost'] = int(match_loss.group(3))
                    result['send'] = int(match_loss.group(1))
                    result['recv'] = int(match_loss.group(2))
                    result['timing'] = int(match_loss.group(4))
                    index += 1
                    if result['lost'] < 100:
                        index += 1
                        match_timing = self.regexp_time.match(self._std_out[index])
                        if match_timing:
                            result['minimum_time'] = int(match_timing.group(1))
                            result['maximum_time'] = int(match_timing.group(3))
                            result['avg_time'] = int(match_timing.group(2))
                            result['mdev'] = int(match_timing.group(4))
                            break
                    else:
                        break
            index += 1
        return result


def create_ping_service(host: str, count: int = 4, packet_size: int = 56, interval: int = 1000):
    if sys.platform == 'win32':
        return SystemWinPing(host, count, packet_size, interval)
    else:
        return SystemLinuxPing(host, count, packet_size, interval)


if __name__ == "__main__":
    pinger = create_ping_service('192.168.88.1')
    print(pinger.run())
