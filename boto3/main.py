import argparse
from argparse import RawTextHelpFormatter
import ec2
import s3
import route53

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument(
    "--resource",
    type=str,
    required=True,
    help="the resource type to manage ( ec2 / s3 / DNS )"
)
parser.add_argument(
    "--action",
    type=str,
    required=True,
    help="the action to make on the resource\n"
         "( for ec2 - create / start / stop / ls,\n"
         "for s3 - create / upload / ls,\n"
         "for DNS - createZ / createR / updateR / deleteR )"
)
parser.add_argument(
    "--instanceName",
    type=str,
    default="new-instance",
    help="the name of the instance to manage"
)
parser.add_argument(
    "--instanceType",
    type=str,
    help="the type of the instance"
)
parser.add_argument(
    "--ami",
    type=str,
    help="the OS for the machine ( Ubuntu / AmazonLinux )"
)
parser.add_argument(
    "--bucketName",
    type=str,
    help="the name of the s3 bucket"
)
parser.add_argument(
    "--access",
    type=str,
    default="private",
    help="the type of access to the s3 bucket ( public / private )"
)
parser.add_argument(
    "--filePath",
    type=str,
    help="the path to the file to upload to the s3 bucket"
)
parser.add_argument(
    "--domainName",
    type=str,
    help="the domain name of the DNS hosted zone ( www.example.com )"
)
parser.add_argument(
    "--recordName",
    type=str,
    help="the subdomain name of the DNS record"
)
parser.add_argument(
    "--recordType",
    type=str,
    help="the type of the DNS record ( 'SOA' | 'A' | 'TXT' | 'NS' | 'CNAME' | 'MX' | 'NAPTR' | 'PTR' | 'SRV' | 'SPF' | 'AAAA' | 'CAA' | 'DS' )"  # 'A' | 'AAAA' | 'CNAME' | 'MX' | 'TXT' | 'PTR' | 'SRV' | 'SPF' | 'NAPTR' | 'CAA'
)
parser.add_argument(
    "--recordValue",
    type=str,
    help="the value of the DNS record"
)
args = parser.parse_args()


def main():
    match args.resource:
        case "ec2":
            ec2.manage_ec2_instances(args)
        case "s3":
            s3.manage_s3_buckets(args)
        case "DNS":
            route53.manage_route53(args)
        case _:
            print("resource not valid, see --help for more information")


main()
