import socket
import struct
import binascii

def normalize_string(x):
    if type(x) == bytes:
        return x.rstrip(b' \t\r\n\0')
    return x

class EcoPlug:
    def __init__(self, pkt):
        self.ip_addr = pkt[0]
        self.mac_addr = pkt[-3]
        self.name = pkt[4].decode('utf-8')
        self.model = pkt[5].decode('utf-8')
        self.fw_ver = pkt[6].decode('utf-8')
        self.plug_data = pkt

    def turn_on(self):
        self._send_command('on')

    def turn_off(self):
        self._send_command('off')

    def is_on(self):
        return self._send_command('state')

    def _send_command(self, cmd):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.ip_addr, 80))
            cmd_str = '{{"system":{{"set_relay_state":{{"state":{}}}}}}}}'.format(1 if cmd == 'on' else 0 if cmd == 'off' else '')
            data = 'POST /upnp/control/BasicService1 HTTP/1.1\r\n' \
                   'Host: {}\r\n' \
                   'Content-Type: text/xml; charset=UTF-8\r\n' \
                   'SOAPAction: "urn:Belkin:service:basicevent:1#SetBinaryState"\r\n' \
                   'Content-Length: {}\r\n\r\n' \
                   '{}'.format(self.ip_addr, len(cmd_str), cmd_str)
            sock.send(data.encode())
            response = sock.recv(1024)
            sock.close()

            return True if b'<BinaryState>1</BinaryState>' in response else False

        except Exception as e:
            print('Error:', e)
            return False
