import datetime
import itertools
import os.path


class FireWallRecord:
    record_time: datetime
    action_allow: bool
    protocol: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    size: int
    tcpflags: int
    tcpsyn: int
    tcpack: int
    tcpwin: int
    icmptype: int
    icmpcode: int
    info: str
    is_recive: bool

    def __init__(self, record_date, data_fields):
        self.record_time = record_date
        self.action_allow = True if data_fields[0] == "ALLOW" else False
        self.protocol = data_fields[1]
        self.src_ip = data_fields[2]
        self.dst_ip = data_fields[3]
        self.src_port = int(data_fields[4]) if data_fields[4] != '-' else 0
        self.dst_port = int(data_fields[5]) if data_fields[5] != '-' else 0
        self.size = int(data_fields[6]) if data_fields[6] != '-' else 0
        self.tcpflags = int(data_fields[7]) if data_fields[7] != '-' else 0
        self.tcpsyn = int(data_fields[8]) if data_fields[8] != '-' else 0
        self.tcpack = int(data_fields[9]) if data_fields[9] != '-' else 0
        self.tcpwin = int(data_fields[10]) if data_fields[10] != '-' else 0
        self.icmptype = int(data_fields[11]) if data_fields[11] != '-' else 0
        self.icmpcode = int(data_fields[12]) if data_fields[12] != '-' else 0
        self.info = data_fields[13]
        self.is_recive = True if data_fields[14] == "RECEIVE" else False

    def get_dst_part(self):
        if self.protocol == "TCP" or self.protocol == "UDP":
            return f"{self.dst_ip}:{self.dst_port}"
        else:
            return self.dst_ip

    def get_src_part(self):
        if self.protocol == "TCP" or self.protocol == "UDP":
            return f"{self.src_ip}:{self.src_port}"
        else:
            return self.src_ip

    def protocol_info(self):
        return f"{self.protocol}:{self.icmptype}:{self.icmpcode}" if self.protocol == "ICMP" else self.protocol

    def get_time(self):
        return self.record_time.strftime("%H:%M:%S")

    def short_info(self):
        action = "" if self.action_allow else "-DROP!"
        return f"{self.get_time()} [{self.protocol_info()}]{self.get_src_part()}->{self.get_dst_part()} {action}"

    def key_info(self):
        if self.protocol == "ICMP":
            if self.is_recive:
                info_part = f"{self.src_ip} -> !{self.icmptype}"
            else:
                info_part = f"{self.dst_ip} <- !{self.icmptype}"
            return f"ICMP {info_part}"
        else:
            if self.is_recive:
                info_part = f"{self.src_ip} -> {self.dst_port}"
            else:
                info_part = f"{self.get_dst_part()}"
            return f"{self.protocol_info()} {info_part}"

    def info(self):
        return f"{self.get_time()} {self.key_info()}"


class DictCounter:
    def __init__(self) -> None:
        super().__init__()
        self.counter_dict = {}

    def put(self, element: FireWallRecord):
        key = element.key_info()
        self.counter_dict[key] = self.counter_dict.get(key, 0) + 1


class FlowAnaliser:
    def __init__(self) -> None:
        super().__init__()
        self.dropped_packets = DictCounter()
        self.processed_packets = DictCounter()

    def add_packet_info(self, connection_info: FireWallRecord):
        if connection_info.action_allow:
            self.processed_packets.put(connection_info)
        else:
            self.dropped_packets.put(connection_info)

    def get_summary_dropped(self, limit=0):
        return self._summary_process(self.dropped_packets, limit)

    def get_summary_processed(self, limit=0):
        return self._summary_process(self.processed_packets, limit)

    @staticmethod
    def _summary_process(counter: DictCounter, limit=0):
        return sorted([(key, count) for key, count in counter.counter_dict.items() if count > limit],
                      key=lambda el: el[1], reverse=True)

    @staticmethod
    def print_key_info(summary):
        for record in summary:
            print(f"\t{record[0]} = {record[1]}")

    def print_summary(self, limit=5):
        print("PROCESSED PACKETS:")
        self.print_key_info(self.get_summary_processed(limit))
        print("DROPPED PACKETS:")
        self.print_key_info(self.get_summary_dropped(limit))


class TimeAnaliser:
    def __init__(self, time: datetime.datetime, delta: datetime.timedelta):
        self.before = FlowAnaliser()
        self.at = FlowAnaliser()
        self.after = FlowAnaliser()
        self.peak_start = time - delta
        self.peak_end = time + delta

    def add_packet_info(self, connection: FireWallRecord):
        connection_time = connection.record_time

        if connection_time < self.peak_start:
            self.before.add_packet_info(connection)
        elif connection_time > self.peak_end:
            self.after.add_packet_info(connection)
        else:
            self.at.add_packet_info(connection)

    def print_summary(self, limit=5):
        print(f"PACKET BEFORE: {self.peak_start.strftime('%d.%m.%y %H:%M:%S')}")
        self.before.print_summary(limit)
        print(f"PACKET IN: {self.peak_start.strftime('%d.%m.%y %H:%M:%S')} "
              f"- {self.peak_end.strftime('%d.%m.%y %H:%M:%S')}")
        self.at.print_summary(limit)
        print(f"PACKET AFTER: {self.peak_end.strftime('%d.%m.%y %H:%M:%S')}")
        self.after.print_summary(limit)

    def tabular_processed(self, limit=0, method="get_summary_processed"):
        before = map(lambda rec: f"{rec[0]} = {rec[1]}", getattr(self.before, method)(limit))
        at = map(lambda rec: f"{rec[0]} = {rec[1]}", getattr(self.at, method)(limit))
        after = map(lambda rec: f"{rec[0]} = {rec[1]}", getattr(self.after, method)(limit))
        return itertools.zip_longest(before, at, after, fillvalue="")

    @staticmethod
    def _pprint_tabular(records):
        for line in records:
            print(f"{line[0]:<40}|{line[1]:<40}|{line[2]:<40}")

    def print_tabular_summary(self, limit=0):
        header = f" INTERVAL: {self.peak_start.strftime('%d.%m.%y %H:%M:%S')} " \
                 f"- {self.peak_end.strftime('%d.%m.%y %H:%M:%S')} "
        print("="*122)
        print(f"{header:-^122}")
        print(f"{' PROCESSED: ':=^122}")
        print(f"{'BEFORE':^40}|{'AT':^40}|{'AFTER':^40}")
        print(f"{'-'*40}|{'-'*40}|{'-'*40}")
        self._pprint_tabular(self.tabular_processed(limit, "get_summary_processed"))
        print(f"{' DPOPPED: ':=^122}")
        print(f"{'BEFORE':^40}|{'AT':^40}|{'AFTER':^40}")
        print(f"{'-' * 40}|{'-' * 40}|{'-' * 40}")
        self._pprint_tabular(self.tabular_processed(limit, "get_summary_dropped"))
        print(f"{'='*122}")


class LogParser:
    def __init__(self, log_file_path):
        self.log_file = log_file_path
        if not os.path.exists(log_file_path):
            raise ValueError(f'Path {log_file_path} - does`n exist!')

    def __iter__(self):
        self.file_desc = open(self.log_file, "rt")
        index = 0
        while True:
            line = self.file_desc.readline()
            index += 1
            if line.startswith("#Fields:") or index > 4:
                break
        return self

    def __next__(self):
        while True:
            line = self.file_desc.readline()
            if line:
                record = line.strip().split()
                if record:
                    date, time, *data = record
                    record_date = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M:%S")
                    return FireWallRecord(record_date, data)
                else:
                    continue
            else:
                self.file_desc.close()
                raise StopIteration()


if __name__ == "__main__":
    #path_file = "D:\\USER_DATA\\Serhii\\OneDrive\\ERC\\WWW01_FIREWALL\\14_00_20_07_23\\pfirewal_inetl.log"
    #path_file = "D:\\USER_DATA\\Serhii\\OneDrive\\ERC\\WWW01_FIREWALL\\14_00_20_07_23\\pfirewall_domain.log"
    path_file = "D:\\USER_DATA\\Serhii\\OneDrive\\ERC\\WWW01_FIREWALL\\23_07_23\\pfirewal_inetl.log"
    #path_file = "D:\\USER_DATA\\Serhii\\OneDrive\\ERC\\WWW01_FIREWALL\\23_07_23\\pfirewall_domain.log"
    log_parser = LogParser(path_file)

    flow = FlowAnaliser()
    time_flow = TimeAnaliser(datetime.datetime.strptime("23.07.23 14:01:30", "%d.%m.%y %H:%M:%S"),
                             datetime.timedelta(minutes=1))
    from_date = datetime.datetime.strptime("23.07.23 12:50:30", "%d.%m.%y %H:%M:%S")
    to_date = datetime.datetime.strptime("23.07.23 22:10:30", "%d.%m.%y %H:%M:%S")
    for line in log_parser:
        if to_date >= line.record_time >= from_date:
            flow.add_packet_info(line)
            time_flow.add_packet_info(line)
            if line.src_ip == "91.219.60.108":
                print(line.record_time)


    flow.print_summary(25)
    time_flow.print_tabular_summary(25)
