"""Controller abstraction for interacting with a Power PMAC over SSH (gpascii).

Provides:
    - Connection management (open / close SSH, launch gpascii)
    - Non blocking buffered reads of stdout / stderr
    - Command send + response parsing with simple synchronization
    - Convenience motion helpers (absolute / relative / limit moves)
    - Basic status queries (position, velocity, in-position, max speed)
    - Gather start / end helpers for data acquisition
    - Homing / phasing / initialization routine

Notes / Assumptions:
    - A single interactive gpascii channel is used (stdin/stdout/stderr) for most commands.
    - Gather export is launched with a separate exec_command. The current implementation
        blocks on reading its stdout (stdout.read()) until the export completes.
    - Error handling is minimal; stderr lines are captured and any non-empty content causes an assert.
    - Timing sleeps (e.g. after enabling gather, during initialisation) are empirical and could be
        refined or replaced with state polling for robustness.
"""

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
    """High-level wrapper around Paramiko SSH session to a Power PMAC.

    Exposes motion and data-gather operations as simple Python methods.
    Internal buffers accumulate stdout until terminators are detected ("Input" on connect,
    or '\x06' for command acknowledgements). Methods generally raise via asserts on sync
    or stderr issues rather than structured exceptions.
    """

    def __init__(self, host):
        """Create controller instance.

        host: IP / hostname of the Power PMAC.
        Does not connect immediately; call connect().
        """
        self.host = host
        self.rcv_buffer = ""
        self.err_buffer = [] # ""
        self.send_time = 0
        self.rcv_time = 0
        self.num_sent = 0
        self.num_received = 0
        self.prev_index =0

    def connect(self, username="root", password="deltatau"):
        """Establish SSH session and start an interactive gpascii (-2) process.

        Blocks until the initial 'Input' prompt is detected.
        """
        try:
            self.session = paramiko.SSHClient()
            self.session.set_missing_host_key_policy(
                paramiko.AutoAddPolicy())
            self.session.connect(self.host,
                                           username=username,
                                           password=password)

            logger.info("Success, connected.")
            success = True
        except paramiko.AuthenticationException:
            self.d_print("Authentication failed when connecting"
                         f"to {self.host}")
            sys.exit(1)

        self.stdin, self.stdout, self.stderr = \
            self.session.exec_command("gpascii -2", bufsize=8192)

        while self._read_until("Input") == "":
            pass

    def disconnect(self):
        """Close the SSH session and reset internal counters/buffers."""
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
        """Perform a non-blocking read loop until 'termstr' appears in buffer.

        Returns the substring (excluding termstr). If stderr captured lines they
        are logged and trigger an assert.
        """
        # if its not already in the buffer then get more from buffer
        self.read_to_buf()

        if self.err_buffer  != [""]:
            for error in self.err_buffer:
                error_temp = error 
                logger.error(f"std_err:{error_temp}") 

            assert False, f"std_err: {self.err_buffer}"

        response = self._read_buf_until(termstr)  # fast read from buffer
        if response != "":
            self.num_received += 1
        return response

    def _read_buf_until(self, termstr):
        """Search existing rcv_buffer for termstr and slice out consumed segment."""
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
        """Pump any pending stdout/stderr into local buffers (non-blocking)."""
        st_time = time.time()
        # non-blocking read
        self.rcv_buffer += self.nb_read()

        errors = self.nb_read_stderr()

        errors = errors.split("\n")  

        self.err_buffer = errors

        self.rcv_time += time.time() - st_time

    def nb_read(self):
        """Non-blocking read of stdout (up to 1024 bytes)."""
        buffer = ""
        # Only get data if there is data to read in the channel
        if self.stdout.channel.recv_ready():
            rl, wl, xl = select.select([self.stdout.channel], [], [], 0.0)
            if len(rl) > 0:
                buffer = self.stdout.channel.recv(1024).decode("utf-8")

        return buffer

    def nb_read_stderr(self):
        """Non-blocking read of stderr (up to 1024 bytes)."""
        buffer = ""
        # Only get data if there is data to read in the channel
        if self.stderr.channel.recv_stderr_ready():
            buffer = self.stderr.channel.recv_stderr(1024).decode("utf-8")
            print(f"received(stderr): {buffer}")
        return buffer


    def send_receive_low(self, cmd_list, stripchar="\r\n\x06"):
        """Send list of commands and return a dict of raw parsed responses.

        stripchar: characters removed from raw response lines.
        """
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
        """Write a single command line to gpascii stdin and flush."""
        st_time = time.time()
        logger.debug(f"sendin {cmd}")
        self.num_sent += 1
        self.stdin.write(cmd + "\n")
        self.stdin.flush()
        self.send_time += time.time() - st_time

    def process_response(self, response, cmd_expected, stripchar="\r\n\x06"):
        """Filter, validate, and split a raw response.

        Returns [original_cmd, value_or_echo]. Asserts on mismatched echoes.
        """
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
        """Helper: send a single command and return only its value portion."""
        response_dict = self.send_receive_low([cmd])
        response = response_dict[cmd][1]
        return response
    
    def wait_till_done(self, chan):
        """Poll Motor[].InPos until it reports 1 (every 100 ms)."""
        cmd = f"motor[{chan}].inpos"
        inpos_state = int(self.send_receive_with_print(cmd))
        while inpos_state != 1:
            inpos_state = int(self.send_receive_with_print(cmd))
            time.sleep(0.1)
    
    def move_to_pos_wait(self, chan, posn):
        """Absolute move then block until in-position."""
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_pos_relative_wait(self, chan, posn):
        """Absolute move then block until in-position."""
        cmd = f"#{chan}j^{posn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_pos(self, chan, posn):
        """Absolute move (non-blocking)."""
        cmd = f"#{chan}j={posn}"
        self.send_receive_with_print(cmd)

    def move_by_relative_pos_wait(self, chan, relPosn):
        """Relative move then wait until in-position."""
        cmd = f"#{chan}j^{relPosn}"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_pos_wait(self, chan):
        """Jog toward positive end limit and wait until motion completes."""
        cmd = f"#{chan}j+"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_neg_wait(self, chan):
        """Jog toward negative end limit and wait until motion completes."""
        cmd = f"#{chan}j-"
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)

    def move_to_end_neg(self, chan):
        """Jog negative (non-blocking)."""
        cmd = f"#{chan}j-"
        self.send_receive_with_print(cmd)

    def get_pos(self, chan):
        """Return current motor position as float."""
        cmd = f"#{chan}p"
        pos = float(self.send_receive_with_print(cmd))
        return pos
    
    def get_velocity(self, chan):
        """Return current commanded velocity (units per second)."""
        cmd = f"#{chan}v"
        vel = float(self.send_receive_with_print(cmd))
        return vel
    
    def get_maximum_velocity(self,chan):
        """Return configured maximum speed (Motor[].MaxSpeed)."""
        cmd = f"Motor[{chan}].MaxSpeed"
        max_vel = float(self.send_receive_with_print(cmd))
        return 0.004

    def set_velocity(self, chan, vel):
        """Set jog speed (Motor[].JogSpeed) then sleep briefly to let it apply."""
        cmd = f"Motor[{chan}].JogSpeed = {vel}"
        self.send_receive_with_print(cmd)
        time.sleep(1)

    def in_pos(self, chan):
        """Return 1 if motor is in-position else 0."""
        cmd = f"motor[{chan}].inpos"
        inpos_state = int(self.send_receive_with_print(cmd))
        return inpos_state

    def start_gather(self, chan, test_id, meas_item=[]):  # NOTE: mutable default kept (original code)
        """Configure and start a gather acquisition.

        meas_item: list of motor field names to gather (e.g. ["ActVel", "Pos"])
        Gather.Enable sequence:
            0 = disable / reset
            3 = enable & start (captures configured addresses)
        Export is initiated via a separate 'gather' shell command (blocking until done).
        """
        num_items = len(meas_item)
        #setting up the gather command
        self.send_receive_with_print(f"Gather.Enable=0")
        
        self.send_receive_with_print(f"Gather.Period=1")
        # self.send_cmd(f"Gather.MaxSamples={max_sample}")

        for i in range(num_items):
            self.send_receive_with_print(f"Gather.Addr[{i}] = Motor[{chan}].{meas_item[i]}")

        self.send_receive_with_print(f"Gather.Items={num_items}")

        self.send_receive_with_print(f"Gather.Enable=3")

        # Launch gather export of the internal buffer to a file. This blocks until the
        # controller finishes writing the file (stdout.read()). Consider making non-blocking
        # if long captures are required.
        _, stdout, _ = self.session.exec_command(
            f"gather /var/ftp/gather/python_script_{test_id}.txt", get_pty=True)
        stdout.read()  # Wait for export completion

    def end_gather(self, test_id):
        """Stop gather and SFTP the exported file locally as gather_output_<id>.txt.

        Sleeps are retained from original implementation (could be shortened with polling).
        """
        time.sleep(5)
        self.send_receive_with_print(f"Gather.Enable=0")
        time.sleep(5)
        sftp_dataget = self.session.open_sftp()
        sftp_dataget.get(f"/var/ftp/gather/python_script_{test_id}.txt", f"results/gather_output_{test_id}.txt")
        sftp_dataget.close()

    def graceful_exit(self, chan):
        """Abort motion (#k) then re-phase motor."""
        self.send_receive_with_print(f"#{chan}k")
        self.phase(chan)

    def initialise(self, chan, enc):
        """Attempt full initialisation: phase, traverse limits, center, home.

        Returns True on success, False if any exception occurs.
        """
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
            self.home(enc)

            return True
        
        except Exception as e:
            print(f"Error during initialisation: {e}")
            return False

    def home(self, chan):
        """Issue home search (homez)."""
        self.send_receive_with_print(f"#{chan}homez")

    def phase(self, chan):
        """Issue phase commands (power-on sequence)."""
        self.send_receive_with_print(f"#{chan}$")
        time.sleep(0.5)
        self.send_receive_with_print(f"#{chan}j/")
        
    def custom_command_non_blocking(self, chan, cmd: str):
        """$$chan$$ to chan"""
        cmd = cmd.replace("$$chan$$", f"{chan}")
        self.send_receive_with_print(cmd)

    def custom_command_blocking(self, chan, cmd: str):
        """Blocking command for $$chan$$ to chan"""
        cmd = cmd.replace("$$chan$$", f"{chan}")
        self.send_receive_with_print(cmd)
        self.wait_till_done(chan)
        