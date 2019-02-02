def getPortName(ifname_shortcut, chassisNum, slotNum, subSlotNum, portNum):
    # 值是None就返回'',不是None就返回数值+'/'
    g = lambda num: '' if num == None else str(num) + '/'
    ifname_shortcut_dis = '' if ifname_shortcut == None else ifname_shortcut

    return ifname_shortcut_dis+g(chassisNum)+g(slotNum)+g(subSlotNum)+portNum
def mapPortType(vender, port_speed):
    if vender =='华为':
        portType_dict = {
            1:'GigabitEthernet',
            10:'Ten-GigabitEthernet',
            40:'FortyGigE',
            100:'100GE',
            None:'',
        }
        portType = portType_dict[port_speed]
    elif vender =='H3C':
        portType_dict = {
            1: 'GigabitEthernet',
            10: 'Ten-GigabitEthernet',
            40: 'FortyGigE',
            100: '100GE',
            None: '',
        }
        portType = portType_dict[port_speed]
    elif vender =='思科':
        portType_dict = {
            1: 'GigabitEthernet',
            10: 'Ten-GigabitEthernet',
            40: 'FortyGigE',
            100: '100GE',
            None: '',
        }
        portType = portType_dict[port_speed]
    else:
        portType_dict = {
            1: 'GigabitEthernet',
            10: 'Ten-GigabitEthernet',
            40: 'FortyGigE',
            100: '100GE',
            None: '',
        }
        portType = portType_dict[port_speed]

    return portType