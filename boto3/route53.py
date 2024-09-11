import boto3


def manage_DNS_records(args):

    match args.action:
        case "createZ":
            create_DNS_zone(args)
        case "createR":
            create_DNS_record(args)
        case "updateR":
            update_DNS_record()
        case "deleteR":
            delete_DNS_record()
        case _:
            print("action not valid, see --help for more information")


def create_DNS_zone(args):
    print("DNS zone was created")


def create_DNS_record(args):
    print("DNS record was created")


def update_DNS_record(args):
    print("DNS record was updated")


def delete_DNS_record(args):
    print("DNS record was deleted")
