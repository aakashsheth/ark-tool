## ArkTool

ArkTool is a simple Python based command line interface used to provision an Ark server in AWS. The infrastructure is provisioned with Cloudformation.

Cloudformation parameters include:
* `ArkServerName`
* `ArkServerJoinPassword`
* `ArkAdminServerPassword`
* `SSHLocation`
* `AvailabilityZone`
* `ExistingRouteTableId`
* `ExistingVpcId`

The resources provisioned:
* `ArkPublicSubnet`
* `ArkPublicSubnetRouteTableAssociation`
* `ArkServer`
* `ArkSecurityGroup`

### Examples
`run.sh` contains the same commands as found below as well as parameter definitions.
##### Creating a new environment
    $ python ark_tool.py create-env -n $ENV_NAME -j $ENV_JOIN_PASSWORD -a $ENV_ADMIN_PASSWORD -ssh $SSH_LOCATION -az $AZ -rtb $ROUTE_TABLE_ID -vpc $VPC_ID

##### Listing all environments
    $ python ark_tool.py list-env

##### Deleting an environment

    $ python ark_tool.py delete-env -n ARK-MY-ARK-SERVER-us-east-1a

### TODOs
* Add VPC/Route Table to Cloudformation
* Set up parameter store for secrets
* Create IAM role for EC2 (access to ParameterStore, possibly KMS)
* Set up Cloudwatch logs/alarms
