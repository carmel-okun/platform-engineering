import boto3
from datetime import datetime
import ipaddress


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
        print("DNS record was created")


def check_if_value_valid(args):
    match args.recordType.upper():
        case "A" | "AAAA":
            try:
                ip_object = ipaddress.ip_address(args.recordValue)
                return True
            except ValueError:
                return False
        case "CNAME":
            return False
        case "MX":
            return False
        case "TXT":
            return False
        case "PTR":
            return False
        case "SRV":
            return False
        case "SPF":
            return False
        case "NAPTR":
            return False
        case "CAA":
            return False
        case _:
            print("Invalid record type, see --help for more information")
    print("valid")
