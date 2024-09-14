import boto3
from datetime import datetime
import ipaddress
import dns.resolver
import re


def manage_route53(args):

    match args.action:
        case "createZ":
            create_DNS_zone(args)
        case "createR" | "updateR" | "deleteR":
            args.action = args.action[:-1].upper()
            if args.action == "UPDATE":
                args.action = "UPSERT"
            manage_DNS_record(args)
        case _:
            print("action not valid, see --help for more information")


def create_DNS_zone(args):

    if args.domainName is None:
        print("more arguments are expected, see --help for more information")
    elif args.domainName[0:4] != "www." or args.domainName[-4:] != ".com":
        print("Invalid domain name, should be of the template www.example.com")
    elif args.domainName in list_hosted_zones():
        print("the domain name", args.domainName, "is already taken")
    else:
        DNS_zone = boto3.client('route53')
        response = DNS_zone.create_hosted_zone(
            Name=args.domainName,
            VPC={
                'VPCRegion': 'us-east-1',
                'VPCId': 'vpc-06dce5518b8882806'
            },
            CallerReference=str(datetime.timestamp(datetime.now())),
            HostedZoneConfig={
                'Comment': "created by " + 'Pita Pitovsky',  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME'),
                'PrivateZone': True
            },
        )
        print(args.domainName, "DNS hosted zone was created successfully")


def list_hosted_zones():
    hosted_zones_list = []
    response = boto3.client('route53').list_hosted_zones()
    for zone in response['HostedZones']:
        hosted_zones_list.append(zone['Name'][:-1])
    return hosted_zones_list


def list_your_hosted_zones():
    your_hosted_zones_list = []
    response = boto3.client('route53').list_hosted_zones()
    for zone in response['HostedZones']:
        if zone['Config']['Comment'] == "created by " + 'Pita Pitovsky':  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME'),
            your_hosted_zones_list.append(zone['Name'][:-1])
    return your_hosted_zones_list

def manage_DNS_record(args):

    if args.domainName is None or args.recordName is None or args.recordType is None or args.recordValue is None:
        print("more arguments are expected, see --help for more information")
    elif args.domainName not in list_your_hosted_zones():
        print("no such hosted zone as", args.domainName)
    elif args.recordType.upper() not in ['A', 'AAAA', 'CNAME', 'MX', 'TXT', 'PTR', 'SRV', 'SPF', 'NAPTR', 'CAA']:
        print("Invalid record type, see --help for more information")
    elif not check_if_value_valid(args):
        print("Invalid record value, see --help for more information")
    else:
        DNS_record = boto3.client('route53')
        DNS_record.change_resource_record_sets(
            HostedZoneId=DNS_record.list_hosted_zones_by_name(DNSName=args.domainName + ".")['HostedZones'][0]['Id'].split('/')[-1],
            ChangeBatch={
                'Comment': "created by " + 'Pita Pitovsky',  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME'),
                'Changes': [
                    {
                        'Action': args.action,
                        'ResourceRecordSet': {
                            'Name': args.recordName + "." + args.domainName,
                            'Type': args.recordType.upper(),
                            'TTL': 60,
                            'ResourceRecords': [
                                {
                                    'Value': args.recordValue
                                },
                            ]
                        }
                    }
                ]
            }
        )
        print("DNS record was", args.action + "d successfully")


def check_if_value_valid(args):
    match args.recordType.upper():
        case "A" | "AAAA":
            try:
                ip_object = ipaddress.ip_address(args.recordValue)
                return True
            except ValueError:
                return False
        case "CNAME" | "PTR":
            pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$')
            return bool(pattern.match(args.recordValue))
        case "MX":
            parts = args.recordValue.split()
            if len(parts) != 2:
                return False
            priority, domain = parts
            pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$')
            return priority.isdigit() and bool(pattern.match(domain))
        case "TXT" | "SPF":
            return isinstance(args.recordValue, str)
        case "SRV":
            parts = args.recordValue.split()
            if len(parts) != 6:
                return False
            service, proto, priority, weight, port, target = parts
            pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$')
            return (
                    service.startswith('_') and
                    proto.startswith('_') and
                    priority.isdigit() and
                    weight.isdigit() and
                    port.isdigit() and
                    bool(pattern.match(target))
            )
        case "NAPTR":
            parts = args.recordValue.split()
            if len(parts) != 6:
                return False
            order, preference, flags, service, regex, replacement = parts
            return (
                    order.isdigit() and
                    preference.isdigit() and
                    flags in ['u', 's'] and
                    service.startswith('E2U+') and
                    replacement.startswith('sip:')
            )
        case "CAA":
            parts = args.recordValue.split()
            if len(parts) != 3:
                return False
            flags, tag, value = parts
            pattern = re.compile(r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$')
            return (
                    flags.isdigit() and
                    tag in ['issue', 'issuewild', 'iodef'] and
                    bool(pattern.match(value.strip('"')))
            )
        case _:
            print("Invalid record type, see --help for more information")
    print("valid")
