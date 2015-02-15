#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#   Author  :   wuyanjun 00291783
#   E-mail  :   wu.wu@hisilicon.com
#   Date    :   14/12/30 16:49:08
#   Desc    :  
#

import sys
import os
import re
import subprocess
import socket

from caliper.client.shared.utils import *
from caliper.client.shared import error

def get_host_arch(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)

def get_host_name(host):
    try:
        arch_result = host.run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            machine_name = output.split(" ")[1]
            return machine_name
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)

def get_host_hardware_info(host):
    hardware_info = {}
    try:
        cpu_type = host.run("grep 'model name' /proc/cpuinfo |uniq |awk -F : '{print $2}' |sed 's/^[ \t]*//g' |sed 's/ \+/ /g'")
        physical_cpu = host.run("grep 'physical id' /proc/cpuinfo |sort |uniq |wc -l")
        logic_cpu = host.run("grep 'processor' /proc/cpuinfo |sort |uniq |wc -l")
        memory = host.run("free -m |grep 'Mem:' |awk -F : '{print $2}' |awk '{print $1}'")
        os_version = host.run("uname -s -r -m")
    except error.CmdError, e:
        logging.info(e.args[0], e.args[1])
        return None
    else:
        if not cpu_type.exit_status:
            hardware_info['CPU_type'] = cpu_type.stdout.split("\n")[0]
        if not physical_cpu.exit_status:
            hardware_info['physical_CPU'] = physical_cpu.stdout.split("\n")[0]
        if not logic_cpu.exit_status:
            hardware_info['logic_CPU'] = logic_cpu.stdout.split("\n")[0]
        if not memory.exit_status:
            hardware_info['Memory'] = memory.stdout.split("\n")[0]
        if not os_version.exit_status:
            hardware_info['OS_Version'] = os_version.stdout.split("\n")[0]
        return hardware_info

def get_local_machine_arch():
    try:
        arch_result = run("/bin/uname -a")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = arch_result.exit_status
        if returncode == 0:
            output = arch_result.stdout
            if re.search('x86_64', output):
                return 'x86_64'
            elif re.search('i[36]86', output):
                return 'x86_32'
            elif re.search('aarch64', output):
                return 'arm_64'
            else:
                if re.search('arm_32', output) or re.search('armv7', output):
                    return 'arm_32'
        else:
            msg = "Caliper does not support this kind of arch machine"
            raise error.ServUnsupportedArchError(msg)

def get_target_ip(target):
    try:
        ip_result = target.run("ifconfig")
    except error.CmdError, e:
        raise error.ServRunError(e.args[0], e.args[1])
    else:
        returncode = ip_result.exit_status
        if returncode==0:
            ip = re.search('\d+\.\d+\.\d+\.\d+', ip_result.stdout).group(0)
            if ip:
                return ip
        return None

def get_local_ip():
    #try:
    #    import socket, fcntl, struct
    #    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15]))   
    #    ret = socket.inet_ntoa(inet[20:24])
    #    return ret
    #except Exception, e:
    #    import socket
    #    hostname = socket.getfqdn()
    #    local_ip = socket.gethostbyname(hostname)
    #    return local_ip
    #return "127.0.1.1"
    cmd_output = commands.getoutput('ifconfig')
    obtain_ip = re.search('\d+\.\d+\.\d+\.\d+', cmd_output).group(0)
    if obtain_ip:
        return obtain_ip
    else:
        return "127.0.1.1"

def sh_escape(command):
    """
    Escape special characters from a command so that it can be passed
    as a double quoted (" ") string in a (ba)sh command
    """
    command = command.replace("\\", "\\\\")
    command = command.replace("$", r'\$')
    command = command.replace('"', r'\"')
    command = command.replace('`', r'\`')
    return command

def get_server_dir():
    path = os.path.dirname(sys.modules['caliper.server.utils'].__file__)
    return os.path.abspath(path)


def scp_remote_escape(filename):
    """
    Escape special characters from a filename so that it can be passed
    to scp (within double quotes) as a remote file.
   
    Bis-quoting has to be used with scp for remote files, "bis-quoting"
    as in quoting x 2
    scp does not support a newline in the filename

    Args:
        filename: the filename string to escape.

    Returns:
        The escaped filename string. The required englobing double
        quotes are NOT added and so should be added at some point by
        the caller.
    """
    escape_chars = r' !"$&' "'" r'()*,:;<=>?[\]^`{|}'

    new_name = []
    for char in filename:
        if char in escape_chars:
            new_name.append("\\%s" % (char,))
        else:
            new_name.append(char)

    return sh_escape("".join(new_name))

def parse_machine(machine, user='root', password='', port=22, profile=''):
    """
    Parser the machine string user:password@host:port and return it separately.
    """
    if '@' in machine:
        user, machine = machine.split('@', 1)
    if ':' in user:
        user, password = user.split(':', 1)
    if ':' in machine:
        machine, port = machine.split(':', 1)
        try:
            port = int(port)
        except ValueError:
            port, profile = machine.split('#', 1)
            port = int(port)

    if '#' in machine:
        machine, profile = machine.split('#', 1)

    if not machine or not user:
        return ValueError

    return machine, user, password, port, profile

