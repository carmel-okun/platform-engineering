import os
import boto3
import botocore.exceptions


def manage_s3_buckets(args):

    match args.action:
        case "create":
            check_if_able_s3_bucket_create(args)
        case "upload":
            upload_to_s3_bucket(args)
        case "ls":
            list_s3_buckets()
        case _:
            print("action not valid, see --help for more information")


def check_if_able_s3_bucket_create(args):

    if args.bucketName is None:
        print("more arguments are expected, see --help for more information")
    else:
        if args.access == "public":
            confirmation = input("Are you sure? [y/N]:").strip().lower()
            if confirmation in ['no', 'n']:
                print("aborted")
            elif confirmation in ['yes', 'y']:
                args.access = "public-read"
                create_s3_bucket(args)
            else:
                print("Invalid input, expecting [yes/y/NO/N]")
        elif args.access == "private":
            create_s3_bucket(args)
        else:
            print("access not valid, see --help for more information")


def create_s3_bucket(args):

    try:
        s3 = boto3.client("s3")
        s3.create_bucket(
            ACL=args.access,
            Bucket=args.bucketName
        )
        s3.put_bucket_tagging(
            Bucket=args.bucketName,
            Tagging={
                'TagSet': [
                    {
                        'Key': 'Owner',
                        'Value': 'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                    },
                ]
            }
        )
        print(args.bucketName, args.access, "bucket was created successfully")
    except botocore.exceptions.ClientError as e:
        if 'BucketAlreadyExists' in str(e):
            print("the bucket name", args.bucketName, "is already taken")
        elif 'BucketAlreadyOwnedByYou' in str(e):
            print("the bucket name", args.bucketName, "is already owned by you")


def upload_to_s3_bucket(args):

    if args.filePath is None or args.bucketName is None:
        print("more arguments are expected, see --help for more information")
    elif args.bucketName not in collect_only_owned_s3_buckets():
        print("no such bucket as", args.bucketName)
    else:
        try:
            s3 = boto3.client("s3")
            s3.upload_file(
                args.filePath,
                args.bucketName,
                os.path.basename(args.filePath)
            )
            print(os.path.basename(args.filePath), "file was uploaded to", args.bucketName, "bucket successfully")
        except FileNotFoundError:
            print(os.path.basename(args.filePath), "file not found, please check the filePath argument and try again")


def list_s3_buckets():

    owned_buckets = collect_only_owned_s3_buckets()
    print("your buckets:")
    print(owned_buckets)


def collect_only_owned_s3_buckets():
    s3 = boto3.client("s3")
    response = s3.list_buckets()

    buckets = response['Buckets']

    buckets_with_tag = []

    for bucket in buckets:
        bucket_name = bucket['Name']

        try:
            tags_response = s3.get_bucket_tagging(Bucket=bucket_name)

            for tag in tags_response.get('TagSet', []):
                if tag['Key'] == "Owner" and tag['Value'] == "Pita Pitovsky":  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                    buckets_with_tag.append(bucket_name)

        except Exception:
            pass

    return buckets_with_tag
