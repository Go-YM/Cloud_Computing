import boto3
from botocore.exceptions import WaiterError

access_key=""
secret_key =""

global ec2
global resource
global ssm

def init_aws():
    #AWS SDK module init
    global ec2
    global resource
    global ssm

    ec2 = boto3.client('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name="us-west-1")
    ssm = boto3.client('ssm',aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name="us-west-1")
    resource = boto3.resource('ec2',aws_access_key_id=access_key,aws_secret_access_key=secret_key,region_name="us-west-1")
    

def listInstances():
    print("Listing instances...")
    done = False
    while done==False:
        list=resource.instances.all()
        for instance in list:
            print("[id] %s, [AMI] %s, [type] %s, [state] %10s, [monitoring state] %s" % (instance.instance_id,instance.image_id,instance.instance_type,instance.state['Name'],instance.monitoring['State']))

        done=True

def availableZones():
    print("Available zones...")
    done = False
    while done==False:
        res=ec2.describe_availability_zones()
        list=res['AvailabilityZones']
        for zone in list:
            print("You have access to [id] %s  [region] %15s [zone] %15s Availability Zones.\n" % (zone['ZoneId'], zone['RegionName'], zone['ZoneName']))

        done=True

def startInstance(id):
    print("Starting .... %s" % id)
    done= False
    while done==False:
        res=ec2.start_instances(InstanceIds=[id])
        instance=resource.Instance(id)
        instance.wait_until_running(Filters=[{'Name': 'instance-id','Values':[id]}])
        print("Successfully started instance %s" % id)
        done=True

def availableRegions():
    print("Available regions...")
    done = False
    while done==False:
        res=ec2.describe_regions()
        list=res['Regions']
        for region in list:
            print("[region] %15s, [endpoint] %s" % (region['RegionName'],region['Endpoint']))

        done=True

def stopInstance(id):
    print("Stopping .... %s" % id)
    done= False
    while done==False:
        res=ec2.stop_instances(InstanceIds=[id])
        instance=resource.Instance(id)
        instance.wait_until_stopped(Filters=[{'Name': 'instance-id','Values':[id]}])
        print("Successfully stopped instance %s" % id)
        done=True

def createInstance(id):
     print("Creating...")
     done= False
     while done==False:
        res=resource.create_instances(ImageId=id,InstanceType='t2.micro',MaxCount=1,MinCount=1,SecurityGroupIds=['sg-0aea1701a877c2c1d'])
        instance=resource.Instance(res[0].instance_id)
        instance.wait_until_running(Filters=[{'Name': 'instance-id','Values':[res[0].instance_id]}])
        print("Successfully started EC2 instance %s based on AMI %s" % (res[0].instance_id,id))
        done=True

def rebootInstance(id):
    print("Rebooting .... %s" % id)
    done= False
    while done==False:
        res=ec2.reboot_instances(InstanceIds=[id])
        instance=resource.Instance(id)
        instance.wait_until_running(Filters=[{'Name': 'instance-id','Values':[id]}])
        print("Successfully rebooted instance %s" % id)
        done=True

def listImages():
    print("Listing images ....")
    done = False
    while done==False:
        res=ec2.describe_images(Filters=[{'Name':'name','Values':['aws-htcondor-slave']}])
        list=res['Images']
        for image in list:
            print("[ImageID] %s, [Name] %s, [Owner] %s" % (image['ImageId'],image['Name'],image['OwnerId']))

        done=True
        
def condor_status():
    res=ssm.send_command(InstanceIds=['i-00e05eb3d6be3ae71'],DocumentName='AWS-RunShellScript',Parameters={'commands': ['condor_status']})
    command_id = res['Command']['CommandId']

    waiter = ssm.get_waiter("command_executed")
    try:
        waiter.wait(
        CommandId=command_id,
        InstanceId='i-00e05eb3d6be3ae71',
        )
    except WaiterError as ex:
        logging.error(ex)
        return

    print(ssm.get_command_invocation(CommandId=command_id, InstanceId='i-00e05eb3d6be3ae71')['StandardOutputContent']) 

if __name__ == "__main__":
    init_aws()
    while True:
        print("------------------------------------------------------------")
        print("           Amazon AWS Control Panel using SDK               ")
        print("------------------------------------------------------------")
        print("  1. list instance                2. available zones        ")
        print("  3. start instance               4. available regions      ")
        print("  5. stop instance                6. create instance        ")
        print("  7. reboot instance              8. list images            ")
        print("  9. condor status                99. exit                  ")
        print("------------------------------------------------------------")

        print("Enter an integer: ",end="")
        num=int(input())

        if num == 1:
            listInstances()
        
        elif num == 2:
            availableZones()
        
        elif num == 3:
            print("Enter instance id: ",end="")
            id=input()
            startInstance(id)
        
        elif num == 4:
            availableRegions()
        
        elif num == 5:
             print("Enter instance id: ",end="")
             id=input()
             stopInstance(id)
        
        elif num == 6:
            print("Enter ami id: ",end="")
            id=input()
            createInstance(id)
        
        elif num == 7:
             print("Enter instance id: ",end="")
             id=input()
             rebootInstance(id)
        
        elif num == 8:
            listImages()
            
        elif num == 9:
            condor_status()

        elif num == 99:
            print("bye!")
            exit(0)
        else:
            print("concertration!")
