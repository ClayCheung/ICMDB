# encoding:utf-8

import IPy, re


def range2list(ipRange):
    ip_list = []

    ipRange = ipRange.strip()

    res = re.search('-', ipRange)
    if res == None:
        # ip+netmask类型
        ipr = IPy.IP(ipRange)

        for x in ipr:
            ip_list.append(str(x))
    else:
        # 指定范围的类型
        first_ip = ipRange.split('-')[0]
        ip_parse = first_ip.rsplit('.', 1)

        for d in range(int(ip_parse[1]), int(ipRange.split('-')[1])+1):
            ip = ip_parse[0] + '.' + str(d)
            ip_list.append(ip)
    return ip_list