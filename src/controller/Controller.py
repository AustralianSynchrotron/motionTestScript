
import logging
import time
import paramiko
import sys
import select
import numpy as np
import pandas as pd
import paramiko.client as client

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
        print(success)

        # wait until gpascii ready
        while self._read_until("Input") == "":
            pass

    def disconnect(self):
        """ close the connection """
        self.session.close()
        logger.info("Disconnected.")
        self.rcv_buffer = ""
        self.err_buffer = [] # ""
        self.send_time = 0
        self.rcv_time = 0
        self.num_sent = 0
        self.num_received = 0
        self.prev_index = 0
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.session = None
        logger.info("Success, disconnected.")


    def _read_until(self, termstr):
        """ a non-async single non-blocking read into rcv_buffer and
        will return the string up to termstr off the buffer if available """
        # if its not already in the buffer then get more from buffer
        self.read_to_buf()

        if self.err_buffer  != [""]:
            for error in self.err_buffer:
                # error_temp = error.decode("utf-8")
                error_temp = error # .decode("utf-8")
                logger.error(f"std_err:{error_temp}") #self.err_buffer}")

            #self.err_buffer = [] #""
            assert False, f"std_err: {self.err_buffer}"

        response = self._read_buf_until(termstr)  # fast read from buffer
        if response != "":
            self.num_received += 1
        return response

    def _read_buf_until(self, termstr):
        ack_pos = self.rcv_buffer.find(termstr)
        if ack_pos == -1:
            return ""
        response = self.rcv_buffer[0:ack_pos]
        ack_pos = ack_pos + len(termstr)  # increment past "\x06"

        if ack_pos >= len(self.rcv_buffer):
            ack_pos = len(self.rcv_buffer)

        self.rcv_buffer = self.rcv_buffer[ack_pos:]

        return response

    def read_to_buf(self):
        """just get any data off ssh and put into local buffer """
        st_time = time.time()
        # non-blocking read
        self.rcv_buffer += self.nb_read()

        errors = self.nb_read_stderr()

        errors = errors.split("\n")  

        self.err_buffer = errors

        self.rcv_time += time.time() - st_time

    def nb_read(self):
        """non-blocking read
        returns whatever in stdout, up to 1024 bytes"""
        buffer = ""
        # Only get data if there is data to read in the channel
        if self.stdout.channel.recv_ready():
            rl, wl, xl = select.select([self.stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                buffer = self.stdout.channel.recv(1024).decode("utf-8")

        return buffer

    def nb_read_stderr(self):
        """ non-blocking read of stderr"""
        buffer = ""
        # Only get data if there is data to read in the channel
        if self.stderr.channel.recv_stderr_ready():
            buffer = self.stderr.channel.recv_stderr(1024).decode("utf-8")
            print(f"received(stderr): {buffer}")
        return buffer


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

    def send_cmd(self, cmd):
        """ send """
        st_time = time.time()
        logger.debug(f"sendin {cmd}")
        self.num_sent += 1
        self.stdin.write(cmd + "\n")
        self.stdin.flush()
        self.send_time += time.time() - st_time

    def process_response(self, response, cmd_expected, stripchar="\r\n\x06"):
        """ takes raw string from ppmac, and finters and checks
        returns [cmd, response] pair"""
        # strip off undesired char
        for char in stripchar:
            response = response.replace(char, "")
    
        if response == "":
            #assert response != "", 
            logger.info(f"sync error, empty response from cmd= {cmd_expected}")

        if response.find("=") != -1:
            cmd_response = [cmd_expected, response.split("=")[1]]
            intended_cmd = cmd_expected.lower()
            cmd_received = response.split("=")[0].lower()
            assert cmd_received == intended_cmd, f"sync error, {response.split('=')[0]} != {cmd_expected}"
        else:
            cmd_response = [cmd_expected, response]
        
        return cmd_response

    def send_receive_with_print(self, cmd):
        response_dict = self.send_receive_low([cmd])

        # strip out the command strings.
        response = response_dict[cmd][1]
        # response_dict contains dictionary of commands sent, and their response.
    
        #print(f"sent \" {cmd} \"")
        #print(f"response \" {response} \"")
        return response
    
    def wait_till_done(self, chan):
        
        cmd = f"motor[{chan}].inpos"
        inpos_state = int(self.send_receive_with_print(cmd))
        while inpos_state != 1:
            inpos_state = int(self.send_receive_with_print(cmd))
            time.sleep(0.1)
        #print("DONE!")
    
    def move_to_pos_wait(self, chan, posn):
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_pos(self, chan, posn):
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)

    def move_by_relative_pos_wait(self, chan, relPosn):
        cmd = f"#{chan}j^{relPosn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_pos_wait(self, chan):
        cmd = f"#{chan}j+"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_neg_wait(self, chan):
        cmd = f"#{chan}j-"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_neg(self, chan):
        cmd = f"#{chan}j-"
        self.send_receive_with_print(cmd)

    def get_pos(self, chan):
        cmd = f"#{chan}p"
        pos = float(self.send_receive_with_print(cmd))
        return pos
    
    def get_velocity(self, chan):
        cmd = f"#{chan}v"
        vel = float(self.send_receive_with_print(cmd))
        return vel
    
    def get_maximum_velocity(self,chan):
        cmd = f"Motor[{chan}].MaxSpeed"
        max_vel = float(self.send_receive_with_print(cmd))
        return max_vel

    def set_velocity(self, chan, vel):
        cmd = f"Motor[{chan}].JogSpeed = {vel}"
        self.send_receive_with_print(cmd)
        time.sleep(1)

    def zero_out(self, chan):
        cmd = f"motor[{chan}].zero" # check this actual command
        self.send_receive_with_print(cmd)
        time.sleep(1)

    def in_pos(self, chan):
        cmd = f"motor[{chan}].inpos"
        inpos_state = int(self.send_receive_with_print(cmd))
        return inpos_state
    
    """
    def current_fetch(self, chan, time_period, time_step):
        times = np.arange(0,time_period,time_step)
        currents = []
        for i in range(len(times)):
            cmd = f"motor[{chan}].IqMeas"
            current_ADC = float(self.send_receive_with_print(cmd))
            sensor_scaling_factor = 1/1000  # Example scaling factor, adjust as needed
            current = current_ADC * sensor_scaling_factor
            currents.append(current)
            time.sleep(0.01)
        return currents
    """

    def start_gather(self, chan, test_id, meas_item=[]):
        num_items = len(meas_item)
        #setting up the gather command
        self.send_receive_with_print(f"Gather.Enable=0")
        
        self.send_receive_with_print(f"Gather.Period=1")
        # self.send_cmd(f"Gather.MaxSamples={max_sample}")

        for i in range(num_items):
            self.send_receive_with_print(f"Gather.Addr[{i}] = Motor[{chan}].{meas_item[i]}")

        self.send_receive_with_print(f"Gather.Items={num_items}")

        self.send_receive_with_print(f"Gather.Enable=3")
        #channel = self.session.invoke_shell(term='xterm')
        _, stdout, _ = self.session.exec_command(f"gather /var/ftp/gather/python_script_{test_id}.txt", get_pty=True)


        stdout.read()

        print("Thread closing")
        #time.sleep(20)

        # self.move_to_pos_wait(2,10)
        # time.sleep(10)
        # self.send_receive_with_print(f"Gather.Enable=0")
        # sftp_dataget = self.session.open_sftp()
        # sftp_dataget.get("/var/ftp/gather/python_script.txt", "current_output")


    def end_gather(self, test_id):
        #stop recording
        time.sleep(10)
        self.send_receive_with_print(f"Gather.Enable=0")
        time.sleep(10)
        #saving the data into file
        sftp_dataget = self.session.open_sftp()
        sftp_dataget.get(f"/var/ftp/gather/python_script_{test_id}.txt", f"gather_output_{test_id}.txt")
        sftp_dataget.close()
        
        #read data
        #df = pd.read_csv(save_to_filename, delim_whitespace=True, header=None)
        #if len(df.columns) != len(meas_item):
        #    raise ValueError(f"Expected {len(meas_item)} columns, got {len(df.columns)}")
        #df.columns = meas_item
        #
        #if as_tuple:
        #    return tuple(df[col] for col in df.columns)
        
        #return df
        

    def graceful_exit(self, chan):
        self.send_cmd(f"#{chan}k")
        self.phase(chan)

    def initialise(self, chan):
        try: 
            self.phase(chan)
            time.sleep(1)

            self.move_to_end_neg_wait(chan)
            neg_pos = self.get_pos(chan)
            self.move_to_end_pos_wait(chan)
            pos_pos = self.get_pos(chan)

            middle_pos = (neg_pos + pos_pos) / 2
            self.move_to_pos_wait(chan, middle_pos)

            self.home(chan)

            return True
        
        except Exception as e:
            print(f"Error during initialisation: {e}")
            return False

    def home(self, chan):
        self.send_cmd(f"#{chan}homez")

    def phase(self, chan):
        self.send_cmd(f"#{chan}$")
        self.send_cmd(f"#{chan}j/")
        





        
        
    
#ppmac = Controller(host="10.23.231.3")
#ppmac.connect()
#chan = 9
#posn = ppmac.get_pos(chan)
#print(posn)
# posn += 10 # increment by 1 [mm]
# ppmac.move_to_pos_wait(chan, posn)
# posn = ppmac.get_pos(chan)
#ppmac.set_velocity(chan, 0.01)
#posn += 10
#ppmac.move_to_pos(chan, posn)
#ppmac.get_velocity(chan)
#ppmac.wait_till_done(chan)
#posn = ppmac.get_pos(chan)