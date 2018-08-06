import fileinput

from puci import *

from common.log import *
from common.env import *

UCI_INTERFACE_CONFIG="interfaceConfig"
UCI_INTERFACE_V4ADDR_CONFIG="interfaceV4addrConfig"


'''
InterfaceConfig
'''
def interface_config_common_get(ifname, interface_data):

    uci_config = ConfigUCI(UCI_INTERFACE_CONFIG, ifname)

    uci_config.show_uci_config(ifname)

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        interface_data[map_key] = map_val[2]

    return interface_data

def interface_config_common_set(req, ifname, interface_data):

    uci_config = ConfigUCI(UCI_INTERFACE_CONFIG, ifname)

    uci_config.set_uci_config(req)

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        if interface_data:
            interface_data[map_key] = map_val[2]

    return interface_data


def interface_config_v4addr_get(ifname, interface_data):
    addr_data = dict()

    uci_config = ConfigUCI(UCI_INTERFACE_V4ADDR_CONFIG, ifname)

    uci_config.show_uci_config(ifname)

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        addr_data[map_key] = map_val[2]

    interface_data['v4addr'] = addr_data

    log_info(LOG_MODULE_SAL, interface_data)

    return interface_data


def interface_config_v4addr_set(req, ifname, interface_data):
    addr_data = dict()

    uci_config = ConfigUCI(UCI_INTERFACE_V4ADDR_CONFIG, ifname)

    uci_config.set_uci_config(req)

    for map_key in uci_config.section_map.keys():
        map_val = uci_config.section_map[map_key]
        addr_data[map_key] = map_val[2]

    interface_data['v4addr'] = addr_data

    return interface_data

def puci_interface_config_retrieve(ifname, add_header):
    if not ifname: return None
    log_info(LOG_MODULE_SAL, "[ifname] : " + ifname)

    interface_data = dict()

    interface_data = interface_config_common_get(ifname, interface_data)
    interface_data = interface_config_v4addr_get(ifname, interface_data)

    if add_header == 1:
        data = {
            'interface' : interface_data,
            'header' : {
                            'resultCode':200,
                            'resultMessage':'Success.',
                            'isSuccessful':'true'
                           }
        }
    else:
        data = interface_data

    return data

def puci_interface_v4addr_config_retrieve(ifname, add_header):
    if not ifname: return None

    interface_data = dict()
    interface_data = interface_config_v4addr_get(ifname, interface_data)

    if add_header == 1:
        data = interface_data
        data['header'] = {
                            'resultCode':200,
                            'resultMessage':'Success.',
                            'isSuccessful':'true'
                           }
    return data


def puci_interface_v4addr_config_create(req, ifname):
    if not ifname: return None

    interface_data = dict()
    interface_data = interface_config_v4addr_set(req, ifname, interface_data)

    data = interface_data
    data['header'] = {
        'resultCode':200,
        'resultMessage':'Success.',
        'isSuccessful':'true'
    }
    return data

def puci_interface_v4addr_config_update(req, ifname):
    if not ifname: return None

    interface_data = dict()
    interface_data = interface_config_v4addr_set(req, ifname, interface_data)

    data = interface_data
    data['header'] = {
        'resultCode':200,
        'resultMessage':'Success.',
        'isSuccessful':'true'
    }
    return data

def puci_interface_config_list():
    iflist=['lan', 'wan', 'wan6']

    for i in range (0, len(iflist)):
        log_info(LOG_MODULE_SAL, "[ifname] : " + iflist[i])
        rc = puci_interface_config_retrieve(iflist[i], 0)
        if i == 0:
            iflist_body = [rc]
        else:
            iflist_body.append(rc)

    data = {
            'interface_list': iflist_body,
            'header' : {
                        'resultCode':200,
                        'resultMessage':'Success.',
                        'isSuccessful':'true'
                       }
            }
    return data


def puci_interface_config_create(reqs):
    reqs_data = reqs['interfaces-list']

    while len(reqs_data) > 0:
        req = reqs_data.pop(0)

        ifname = req['ifname']

        interface_config_common_set(req, ifname, None)
        if "v4addr" in req:
            interface_config_v4addr_set(req['v4addr'], ifname, None)

    data = {
            'header' : {
                        'resultCode':200,
                        'resultMessage':'Success.',
                        'isSuccessful':'true'
                       }
            }

    return data

def puci_interface_config_update(req, ifname):
    if not ifname: return None
    log_info(LOG_MODULE_SAL, "[ifname] : " + ifname)

    interface_data = dict()

    interface_data = interface_config_common_set(req, ifname, interface_data)
    if "v4addr" in req:
        interface_data = interface_config_v4addr_set(req['v4addr'], ifname, interface_data)

    data = {
            'interface_list': interface_data,
            'header' : {
                        'resultCode':200,
                        'resultMessage':'Success.',
                        'isSuccessful':'true'
                       }
           }
    return data


'''
GenericIfStats
'''
def get_generic_port_traffic(ifname):
    #Get port traffic from /proc/net/dev file
    stats=None
    port_count = 0
    for line in fileinput.input([PROC_NET_DEV_PATH]):
        if not line:
            break
        if not ':' in line:
            continue
        line = line.replace("\n", "")
        token = line.split()

        if ifname:
            if line.find(ifname) == -1:
                continue
            stats = [[ifname, token[1], token[2], token[9], token[10]]]
            break
        else:
            if port_count == 0:
                stats = [[token[0], token[1], token[2], token[9], token[10]]]
            else:
                stats.append([token[0], token[1], token[2], token[9], token[10]])
        port_count = port_count + 1

    fileinput.close()
    return stats, port_count


def generic_ifstats_list():
    stats, port_count = get_generic_port_traffic('')

    for index in range(0, port_count):
        temp = {
                'ifName':stats[index][0],
                'ifIndex':0,
                'rxBytes':stats[index][1],
                'rxPkts':stats[index][2],
                'txBytes':stats[index][3],
                'txPkts':stats[index][4]
        }
        if index == 0:
            ifstats_body = [temp]
        else:
            ifstats_body.append(temp)
        index = index + 1

    data = {
            'traffic-list': ifstats_body,
            'header':{
            'resultCode':200,
            'resultMessage':'Success.',
            'isSuccessful':'true'
            }
    }
    return data


def generic_ifstats_retrieve(ifname):
    if not ifname: return None
    log_info(LOG_MODULE_SAL, "[ifname] : " + ifname)

    stats, port_count = get_generic_port_traffic(ifname)
    if not stats: return None

    ifstats_body = {
            'ifName':stats[0][0],
            'ifIndex':0,
            'rxBytes':stats[0][1],
            'rxPkts':stats[0][2],
            'txBytes':stats[0][3],
            'txPkts':stats[0][4]
    }

    data = {
            'traffic': ifstats_body,
            'header':{
            'resultCode':200,
            'resultMessage':'Success.',
            'isSuccessful':'true'
        }
    }
    return data



