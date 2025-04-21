
import logging
import time
import paramiko
import sys

logger = logging.getLogger(__name__)

class Controller:

    def __init__(self, host):
        self.host = host
        self.rcv_buffer = ""
        self.err_buffer = [] # ""
        self.send_time = 0
        self.rcv_time = 0
        self.num_sent = 0
        self.num_received = 0
        self.prev_index =0

    def connect(self, username="root", password="deltatau"):
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.session.connect(self.host,
                                           username=username,
                                           password=password)
            # see also paramiko timeout=self.TIMEOUT)
            logger.info("Success, connected.")
            success = True
        except paramiko.AuthenticationException:
            self.d_print("Authentication failed when connecting"
                         f"to {self.host}")
            sys.exit(1)

        # 8192 is paramiko default bufsize
        self.stdin, self.stdout, self.stderr = \
            self.session.exec_command("gpascii -2", bufsize=8192)

    def send_cmd(self, cmd):
        """ send """
        st_time = time.time()
        logger.debug(f"sendin {cmd}")
        self.num_sent += 1
        self.stdin.write(cmd + "\n")
        self.stdin.flush()
        self.send_time += time.time() - st_time

    def send_receive_low(self, cmd_list, stripchar="\r\n\x06"):
        """ send a list of commands & receive a list back"""
        for cmd in cmd_list:
            self.send_cmd(cmd)

        out_dict = {}
        reply_num = 0
        while reply_num < len(cmd_list):
            response = self._read_until("\x06")
            if response != "":
                cmd_response = self.process_response(response, cmd_list[reply_num], stripchar=stripchar)
                out_dict[cmd_list[reply_num]] = cmd_response
                reply_num += 1

        return out_dict
    
    def send_receive_with_print(self, cmd):
        response_dict = self.send_receive_low([cmd])

        # strip out the command strings.
        response = response_dict[cmd][1]
        # response_dict contains dictionary of commands sent, and their response.
    
        print(f"sent \" {cmd} \"")
        print(f"response \" {response} \"")
        return response
    
    def wait_till_done(self, chan):
        cmd = f"motor[{chan}].inpos"
        inpos_state = int(self.send_receive_with_print(cmd))
        while (inpos_state) != 1:
            inpos_state = int(self.send_receive_with_print(cmd))
            time.sleep(0.1)
    
    def move_to_pos_wait(self, chan, posn):
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_pos(self, chan, posn):
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)

    def get_pos(self, chan):
        cmd = f"#{chan}p"
        pos = float(self.send_receive_with_print(cmd))
        return pos
    
    def get_velocity(self, chan):
        cmd = f"#{chan}v"
        vel = float(self.send_receive_with_print(cmd))
        return vel

    def set_velocity(self, chan, vel):
        cmd = f"#{chan}v={vel}"
        self.send_receive_with_print(cmd)
    
ppmac = Controller(host="10.209.1.1")
ppmac.connect()
chan = 1
posn = ppmac.get_pos(chan)
posn += 1 # increment by 1 [mm]
ppmac.move_to_pos_wait(chan, posn)
posn = ppmac.get_pos(chan)
ppmac.set_velocity(chan, 10)
posn += 10
ppmac.move_to_pos(chan, posn)
ppmac.get_velocity(chan)
ppmac.wait_till_done(chan)
posn = ppmac.get_pos(chan)