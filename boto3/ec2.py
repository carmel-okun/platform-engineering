import boto3


def manage_ec2_instances(args):

    match args.action:
        case "create":
            check_if_able_ec2_create(args)
        case "start":
            start_ec2_instance(args)
        case "stop":
            stop_ec2_instance(args)
        case "ls":
            list_ec2_instances()
        case _:
            print("action not valid, see --help for more information")


def check_if_able_ec2_create(args):

    num_all_running_instances = get_all_running_instances()

    if args.instanceType is None or args.ami is None:
        print("more arguments are expected, see --help for more information")
    elif args.instanceType not in ["t2.micro", "t3.nano"] or args.ami not in ["Ubuntu", "AmazonLinux"]:
        print("you don't have permission for this instance type or OS, see --help for more information")
    elif num_all_running_instances >= 2:
        print("you have", num_all_running_instances, "running instances, stop one before creating another")
    else:
        create_ec2_instance(args)
        print(args.instanceName, "instance was created successfully")


# function which create the instances
def create_ec2_instance(args):

    if args.ami == "Ubuntu":
        args.ami = "ami-0e86e20dae9224db8"
    else:
        args.ami = "ami-0182f373e66f89c85"

    # create an ec2 client
    ec2 = boto3.resource("ec2")

    # function which create an ec2 instance
    ec2.create_instances(

        # tagging the instance
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': args.instanceName
                    },
                    {
                        'Key': 'Owner',
                        'Value': 'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                    }
                ]
            }
        ],

        # associating the instance with a public IPv4
        NetworkInterfaces=[
            {
                'AssociatePublicIpAddress': True,
                'DeleteOnTermination': True,
                'Description': 'associate public ipv4',
                'DeviceIndex': 0,
                'Groups': [
                    "sg-0dcf9dad4dc751acb",
                ],
                'SubnetId': "subnet-0f748f67d5a99439f",
            }
        ],

        InstanceType=args.instanceType,
        KeyName="carmel-keypem",
        ImageId=args.ami,
        MinCount=1,
        MaxCount=1
    )


def check_if_ec2_exist(args):

    all_insts_name_list = list_instances_names()
    if args.instanceName is None:
        print("instanceName argument is expected, see --help for more information")
        return False
    elif args.instanceName not in all_insts_name_list:
        print("there's no such instance as", args.instanceName)
        print("maybe check your spelling and try again")
        return False
    else:
        return True


def list_instances_names():
    all_insts_name_list = []
    all_instances = get_all_instances()
    reservation_len = len(all_instances)
    for instance in range(reservation_len):
        if all_instances[instance]['Instances'][0]['Tags'][0]['Value'] == "Pita Pitovsky":  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
            all_insts_name_list.append(all_instances[instance]['Instances'][0]['Tags'][1]['Value'])
        else:
            all_insts_name_list.append(all_instances[instance]['Instances'][0]['Tags'][0]['Value'])
    return all_insts_name_list


def start_ec2_instance(args):

    is_exist = check_if_ec2_exist(args)
    if is_exist:
        chosen_inst_detail = find_specified_instance(args)
        chosen_inst_state = chosen_inst_detail['State']['Name']
        chosen_inst_id = chosen_inst_detail['InstanceId']
        if chosen_inst_state != 'stopped':
            print(chosen_inst_id, "is not in the stopped state")
        else:
            ec2 = boto3.client("ec2")
            ec2.start_instances(InstanceIds=[chosen_inst_id])
            print(chosen_inst_id, "has started")


def stop_ec2_instance(args):

    is_exist = check_if_ec2_exist(args)
    if is_exist:
        chosen_inst_detail = find_specified_instance(args)
        chosen_inst_state = chosen_inst_detail['State']['Name']
        chosen_inst_id = chosen_inst_detail['InstanceId']
        if chosen_inst_state != 'running':
            print(chosen_inst_id, "is not in the running state")
        else:
            ec2 = boto3.client("ec2")
            ec2.stop_instances(InstanceIds=[chosen_inst_id])
            print(chosen_inst_id, "has stopped")


def find_specified_instance(args):
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Name',
                'Values': [
                    args.instanceName
                ]
            }
        ]
    )
    chosen_inst_detail = response['Reservations'][0]['Instances'][0]
    return chosen_inst_detail


def list_ec2_instances():
    all_instances = get_all_instances()
    print("your running instances:")
    print(all_instances)


def get_all_instances():
    ec2 = boto3.client("ec2")
    response = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Owner',
                'Values': [
                    'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                ]
            }
        ]
    )
    all_instances = response['Reservations']
    return all_instances


def get_all_running_instances():
    ec2 = boto3.client("ec2")
    running_insts = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Owner',
                'Values': [
                    'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'running'
                ]
            }
        ]
    )
    pending_insts = ec2.describe_instances(
        Filters=[
            {
                'Name': 'tag:Owner',
                'Values': [
                    'Pita Pitovsky'  # os.getlogin() or os.getenv('USER' | 'LOGNAME' | 'USERNAME')
                ]
            },
            {
                'Name': 'instance-state-name',
                'Values': [
                    'pending'
                ]
            }
        ]
    )
    num_running_instances = int(len(running_insts['Reservations']))
    num_pending_instances = int(len(pending_insts['Reservations']))
    num_all_running_instances = num_running_instances + num_pending_instances
    return num_all_running_instances
