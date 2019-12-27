# -*- coding: utf-8 -*-

import boto3
import datetime

ec = boto3.client('ec2')

def handler(event, context):
    Backup()
    Clean(event)


def Backup():
    print("Starting Backup")

    reservations = ec.describe_instances(
        Filters=[
            #{'Name': 'tag-key', 'Values': ['backup', 'Backup']},
            {'Name': 'tag:Backup', 'Values': ['true', 'True']},
            #{'Name': 'instance-state-name', 'Values': ['running']}
        ]
    ).get(
        'Reservations', []
    )

    instances = sum(
        [
            [i for i in r['Instances']]
            for r in reservations
        ], [])

    print("Found %d instances " % len(instances))

    cnt = 0

    for instance in instances:

        #print("State:>" + instance['State']['Name'])

        for dev in instance['BlockDeviceMappings']:
            if dev.get('Ebs', None) is None:
                continue
            vol_id = dev['Ebs']['VolumeId']
            print("Found EBS volume %s on instance %s" % (vol_id, instance['InstanceId']))

            if instance['State']['Name'] == "stopped":
                if CheckStoppedSnap(vol_id) > 0:
                    print("Skip Instance %s is stopped and have already stopped snapshot" % (instance['InstanceId']))
                    continue

            snap = ec.create_snapshot(
                VolumeId=vol_id,
            )

            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == "Name":
                        instance_name = tag['Value']
                    elif tag['Key'] == "Type":
                        instance_type = tag['Value']

            if not instance_name:
                instance_name = ""
            if not instance_type:
                instance_type = ""

            print("Retaining snapshot %s of volume %s from instance %s" %
                  (
                      snap['SnapshotId'],
                      vol_id,
                      instance['InstanceId']
                  )
                  )

            ec.create_tags(
                Resources=[snap['SnapshotId']],
                Tags=[
                    {'Key': 'Name', 'Value': instance_name},
                    {'Key': 'Type', 'Value': instance_type},
                    {'Key': 'StateName','Value': instance['State']['Name']}
                ]
            )
            cnt = cnt + 1
            print("Tagging operation completed.")

    print("Backup Snap: " + str(cnt))
    print("End Backup!")


def Clean(event):
    retention = event.get('retention')
    account_id = event.get('account_id')

    print("Starting Clean...")
    account_ids = [account_id]

    snapshot_response = ec.describe_snapshots(OwnerIds=account_ids)

    cnt = 0
    for snap in snapshot_response['Snapshots']:

        state_name = None

        if 'Tags' in snap:
            for tag in snap['Tags']:
                if tag['Key'] == "StateName":
                    state_name = tag['Value']

        if state_name == "stopped" or state_name == "terminated":
            print("Skip this snapshot because of Stopped/Terminated Instance Snap %s" % (snap['SnapshotId']))
            continue

        a = snap['StartTime']
        b = a.date()
        c = datetime.datetime.now().date()
        d = c - b
        if d.days >= retention:
            try:
                ec.delete_snapshot(SnapshotId=snap['SnapshotId'])
                print("Delete snapshot %s -  %s" % (snap['SnapshotId'], a))
            except Exception as e:
                #print(">>>>" + str(e))
                if 'InvalidSnapshot.InUse' in str(e):
                    print("Skipping this snapshot because of Error: %s" % str(e))
                    continue
            cnt = cnt + 1

    print("Deleted Snap: " + str(cnt))
    print("End Clean!")


def CheckStoppedSnap(volumeId):
    response = ec.describe_snapshots(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': [volumeId]
            },
            {
                'Name': 'tag:StateName',
                'Values': ["stopped"]
            }
        ]
    )
    return len(response['Snapshots'])