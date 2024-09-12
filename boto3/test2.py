import boto3
from datetime import datetime

domainName = 'www.carmel.com'
def create_DNS_zone():
    hosted_zones_list = list_hosted_zones()

    if domainName is None:
        print("more arguments are expected, see --help for more information")
    elif domainName[0:4] != "www." or domainName[-4:] != ".com":
        print("Invalid domain name, should be of the template www.example.com")
    elif domainName in hosted_zones_list:
        print("the domain name", domainName, "is already taken")
    else:
        DNS_zone = boto3.client('route53')
        DNS_zone.create_hosted_zone(
            Name=domainName,
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
        print(domainName, "DNS hosted zone was created successfully")


def list_hosted_zones():
    list_hosted_zones = []
    response = boto3.client('route53').list_hosted_zones()
    for zone in response['HostedZones']:
        list_hosted_zones.append(zone['Name'][:-1])
    return list_hosted_zones

create_DNS_zone()
