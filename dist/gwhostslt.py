#!/usr/bin/env python
from collections import defaultdict, OrderedDict
from logging import getLogger, DEBUG
from logging.handlers import SysLogHandler
from os import system
from socket import gethostbyname_ex
from sys import argv

# setup logging
logger = getLogger('')
logger.setLevel(DEBUG)
logger.addHandler(SysLogHandler(address='/dev/log'))


def addresses2subnets(data):
    """ Aggregate addresses to subnets (up to 16-bit)
        >>> addresses2subnets(
        ...     OrderedDict([('192.168.1.1', ['a.com', 'b.com']), ('172.16.1.2', ['c.com']), ('172.16.3.4', ['d.com'])])
        ... )
        OrderedDict([('172.16.0.0/16', ['c.com', 'd.com']), ('192.168.1.1/32', ['a.com', 'b.com'])])
    """
    subnets = OrderedDict()

    # sort addresses to easily collect subnets:
    # |------- 1st subnet -------|- 2nd subnet -|
    # ['172.16.1.2', '172.16.3.4', '192.168.1.1']
    addresses = sorted(data.keys())

    # split addresses into octets:
    #     0     1     2    3       0     1     2    3       0      1     2    3
    #     |     |     |    |       |     |     |    |       |      |     |    |
    # [['172', '16', '1', '2'], ['172', '16', '3', '4'], ['192', '168', '1', '1']]
    octets = [ip.split('.') for ip in addresses]

    # process addresses
    addr_idx = 0

    while addr_idx < len(octets):
        octet = octets[addr_idx]
        subnet_size = 32

        # add related domains
        domains = set(data[addresses[addr_idx]])

        # look for subnet in following addresses
        next_addr_idx = addr_idx + 1

        while next_addr_idx < len(octets):
            next_octet = octets[next_addr_idx]
            next_subnet_size = 32

            # if the first octets are equal
            if octet[0] == next_octet[0]:

                # if the first two octets are equal, change the subnet size to 16
                if octet[1] == next_octet[1]:
                    next_subnet_size = subnet_size = 16

                    # if the first three octets are equal, change the subnet size to 24
                    if octet[2] == next_octet[2]:
                        next_subnet_size = subnet_size = 24

            # the last address for subnet is detected
            if next_subnet_size == 32:
                break

            # add additional domains
            domains.update(data[addresses[next_addr_idx]])

            # check the next address
            next_addr_idx += 1

        # store subnet
        subnet = '.'.join(octet[:subnet_size // 8] + ['0' for _ in range((32 - subnet_size) // 8)])
        subnets['/'.join((subnet, str(subnet_size)))] = sorted(domains)

        # continue from the next subnet
        addr_idx = next_addr_idx

    return subnets


def hostnames2addresses(hostnames):
    """ Aggregate hostnames and addresses
        >>> hostnames2addresses(['a.com', 'b.com', 'c.com', 'd.com'])
        OrderedDict([('192.168.1.1', ['a.com', 'b.com']), ('172.16.1.2', ['c.com']), ('172.16.3.4', ['d.com'])])
    """
    addresses = defaultdict(set)
    for name in hostnames:
        try:
            # domain aliases 1st address   2nd address
            #    |      |         |             |
            # 'e.com', [], ['172.16.1.2', '172.16.3.4']
            cname, aliases, ip_list = gethostbyname_ex(name)

        except Exception as e:
            logger.exception(e)

        else:
            for ip in ip_list:
                addresses[ip].update(aliases)

    return OrderedDict((key, sorted(addresses[key])) for key in sorted(addresses.keys()))


def add_routes(subnets, gateway):
    """ Add routes for subnets via specified gateway
    """
    for subnet, hostnames in subnets.items():
        err = system('ip r add {subnet} via {gateway}'.format(subnet=subnet, gateway=gateway))

        if not err:
            logger.info('[R] %s[%s] via %s', subnet, ','.join(hostnames), gateway)


if __name__ == '__main__':
    if len(argv) < 3:
        print('Usage: {} <gateway> <hostsfile>'.format(*argv))
        exit(1)

    with open(argv[2], 'r') as gwhosts:
        add_routes(
            subnets=addresses2subnets(hostnames2addresses(name.rstrip('\n') for name in gwhosts.readlines() if name)),
            gateway=argv[1],
        )
