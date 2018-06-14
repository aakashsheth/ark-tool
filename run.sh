#! /bin/bash

ENV_NAME="MY-ARK-SERVER" # Must follow Cloudformation stack naming conventions
ENV_JOIN_PASSWORD="password1"
ENV_ADMIN_PASSWORD="password1"
SSH_LOCATION="68.187.147.57/32"
AZ="us-east-1a"
ROUTE_TABLE_ID="rtb-015d40f73a6249945"
VPC_ID="vpc-0646913daf49fbe9e"

# Create
 # python ark_tool.py create-env -n $ENV_NAME -j $ENV_JOIN_PASSWORD -a $ENV_ADMIN_PASSWORD -ssh $SSH_LOCATION -az $AZ -rtb $ROUTE_TABLE_ID -vpc $VPC_ID

# # List
# python ark_tool.py list-env

# # Delete
python ark_tool.py delete-env -n ARK-MY-ARK-SERVER-us-east-1a
