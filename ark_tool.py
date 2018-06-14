# bin/bash -xe

import logging
import argparse
import json
import sys

import boto3
from botocore.exceptions import ClientError

MANDATORY_TAG = "ARK"
ARK_CFN = "ark_cfn.yaml"


class Ark(object):

    def __init__(self):
        self.cfn = boto3.client("cloudformation")

        parser = argparse.ArgumentParser(
            description="CLI to create an Ark environment",
            usage='''ark <command> [<args>]
            create-env     Create a new environment
            list-env       List all environmenta
            delete-env     Delete an environment
            ''')

        parser.add_argument('command', help="List, create/update, or delete an Ark environment")
        args = parser.parse_args(sys.argv[1:2])

        if args.command == "create-env":
            self.create_or_update_environment()
        elif args.command == "list-env":
            envs = self.list_environments()

            print("Found %s environment(s):" % len(envs))
            for env in envs:
                print("%s" % env["StackName"])

        elif args.command == "delete-env":
            self.delete_environment()
        else:
            print("Unrecognized command")
            parser.print_help()
            exit(1)

    def get_env_by_name(self, name):
        envs = self.list_environments()

        for env in envs:
            if env["StackName"] == name:
                return env

        return {}

    def parse_template(self, template):
        with open(template) as t:
            t_data = t.read()
        self.cfn.validate_template(TemplateBody=t_data)
        return t_data

    def create_or_update_environment(self):
        parser = argparse.ArgumentParser(
            description="Create or update an Ark environment"
        )
        required_args = parser.add_argument_group("Required arguments to create environment")
        required_args.add_argument("-n", "--name", help="Environment name", required=True)
        required_args.add_argument("-j", "--join-password", help="Environment join password", required=True)
        required_args.add_argument("-a", "--admin-password", help="Environment admin password", required=True)
        required_args.add_argument("-ssh", "--ssh-location", help="Ip to grant SSH access", required=True)
        required_args.add_argument("-az", "--availabilty-zone", help="AWS availabilty zone", required=True)
        required_args.add_argument("-rtb", "--route-table-id", help="Existing route table id", required=True)
        required_args.add_argument("-vpc", "--vpc-id", help="Vpc id", required=True)

        args = parser.parse_args(sys.argv[2:])

        env_name = "%s-%s-%s" % (MANDATORY_TAG, args.name, args.availabilty_zone)
        env = self.get_env_by_name(env_name)
        template = self.parse_template(ARK_CFN)

        if not env:
            print("Creating environment: '%s'..." % env_name)
            response = self.cfn.create_stack(
                StackName=env_name,
                TemplateBody=template,
                Parameters=[
                    {
                        "ParameterKey": "ArkServerName",
                        "ParameterValue": args.name,
                    },
                    {
                        "ParameterKey": "ArkServerJoinPassword",
                        "ParameterValue": args.join_password,
                    },
                    {
                        "ParameterKey": "ArkAdminServerPassword",
                        "ParameterValue": args.admin_password,
                    },
                    {
                        "ParameterKey": "SSHLocation",
                        "ParameterValue": args.ssh_location,
                    },
                    {
                        "ParameterKey": "AvailabilityZone",
                        "ParameterValue": args.availabilty_zone,
                    },
                    {
                        "ParameterKey": "ExistingRouteTableId",
                        "ParameterValue": args.route_table_id,
                    },
                    {
                        "ParameterKey": "ExistingVpcId",
                        "ParameterValue": args.vpc_id,
                    },
                ],
                Tags=[
                    {
                        'Key': 'ARK',
                        'Value': args.name
                    },
                ],
            )
            waiter = self.cfn.get_waiter("stack_create_complete")
            waiter.wait(
                StackName=response["StackId"]
            )
            print("Environment creation complete")
            print(json.dumps(response, indent=2, default=str))

        else:
            print("Found env: '%s'" % env)
            try:
                print("Attempting to update environment")
                response = self.cfn.update_stack(
                    StackName=env_name,
                    TemplateBody=template,
                    Parameters=[
                        {
                            "ParameterKey": "ArkServerName",
                            "ParameterValue": args.name,
                        },
                        {
                            "ParameterKey": "ArkServerJoinPassword",
                            "ParameterValue": args.join_password,
                        },
                        {
                            "ParameterKey": "ArkAdminServerPassword",
                            "ParameterValue": args.admin_password,
                        },
                        {
                            "ParameterKey": "SSHLocation",
                            "ParameterValue": args.ssh_location,
                        },
                        {
                            "ParameterKey": "AvailabilityZone",
                            "ParameterValue": args.availabilty_zone,
                        },
                        {
                            "ParameterKey": "ExistingRouteTableId",
                            "ParameterValue": args.route_table_id,
                        },
                        {
                            "ParameterKey": "ExistingVpcId",
                            "ParameterValue": args.vpc_id,
                        },
                    ],
                    Tags=[
                        {
                            'Key': 'ARK',
                            'Value': args.name
                        },
                    ],
                )
                waiter = self.cfn.get_waiter("stack_update_complete")
                waiter.wait(
                    StackName=response["StackId"]
                )
                print("Environment update complete")
                print(json.dumps(response, indent=2, default=str))

            except ClientError as e:
                if "No updates are to be performed" not in e["Message"]:
                    raise e
                print("No updates to perform")

    def list_environments(self):
        stacks = self.cfn.describe_stacks()["Stacks"]

        envs = []
        if stacks:
            for stack in stacks:
                for tag in stack["Tags"]:
                    if tag["Key"] == MANDATORY_TAG:
                        envs.append(stack)

        return envs

    def delete_environment(self):
        parser = argparse.ArgumentParser(
            description="Delete an Ark environment"
        )
        required_args = parser.add_argument_group("Required arguments to delete environment")
        required_args.add_argument("-n", "--name", help="Environment name", required=True)

        args = parser.parse_args(sys.argv[2:])

        try:
            print("Delete environment '%s'" % args.name)
            response = self.cfn.delete_stack(
                StackName=args.name
            )
            waiter = self.cfn.get_waiter("stack_delete_complete")
            waiter.wait(
                StackName=args.name
            )
            print("Environment delete complete")
            print(json.dumps(response, indent=2, default=str))
        except ClientError as e:
            print(e)
        pass


if __name__ == "__main__":
    Ark()
