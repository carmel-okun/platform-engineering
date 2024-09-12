import boto3
from datetime import datetime


def manage_DNS_records(args):

    match args.action:
        case "createZ":
            create_DNS_zone(args)
        case "createR":
            create_DNS_record(args)
        case "updateR":
            update_DNS_record(args)
        case "deleteR":
            delete_DNS_record(args)
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
                # 'Comment': 'string',
                'PrivateZone': True
            },
        )
        DNS_zone.change_tags_for_resource(
            ResourceType='hostedzone',
            ResourceId=response['HostedZone']['Id'].split('/')[-1],
            AddTags=[
                {
                    'Key': 'Owner',
                    'Value': 'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                },
            ]
        )
        print(args.domainName, "DNS hosted zone was created successfully")


def list_hosted_zones():
    hosted_zones_list = []
    response = boto3.client('route53').list_hosted_zones()
    for zone in response['HostedZones']:
        hosted_zones_list.append(zone['Name'][:-1])
    return hosted_zones_list


def create_DNS_record(args):
    print("DNS record was created")


def update_DNS_record(args):
    print("DNS record was updated")


def delete_DNS_record(args):
    print("DNS record was deleted")
