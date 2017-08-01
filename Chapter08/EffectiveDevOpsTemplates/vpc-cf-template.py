"""Generating CloudFormation template."""

from troposphere import (
    GetAZs,
    Output,
    Parameter,
    Ref,
    Select,
    Sub,
    Tags,
    Template,
    GetAtt
)

from troposphere.ec2 import (
    VPC,
    InternetGateway,
    NetworkAcl,
    NetworkAclEntry,
    Route,
    RouteTable,
    Subnet,
    SubnetNetworkAclAssociation,
    SubnetRouteTableAssociation,
    VPCGatewayAttachment,
    EIP,
    NatGateway,
)

t = Template()

t.add_description("Effective DevOps in AWS: VPC, public and private subnets")

t.add_parameter(Parameter(
    "ClassB",
    Type="Number",
    Description="Class B of VPC (10.XXX.0.0/16)",
    Default="0",
    MinValue=0,
    MaxValue=255,
    ConstraintDescription="Must be in the range [0-255]",
))

t.add_resource(VPC(
    "VPC",
    EnableDnsSupport="true",
    EnableDnsHostnames="true",
    CidrBlock=Sub('10.${ClassB}.0.0/16'),
    Tags=Tags(
        Name=Ref("AWS::StackName"),
    )
))

t.add_resource(InternetGateway(
    "InternetGateway",
    Tags=Tags(
        Name=Ref("AWS::StackName"),
    )
))

t.add_resource(VPCGatewayAttachment(
    "VPNGatewayAttachment",
    VpcId=Ref("VPC"),
    InternetGatewayId=Ref("InternetGateway")
))

accessibility = ["Private", "Public"]
names = ["A", "B", "C", "D"]
count = 0

for a in accessibility:
    t.add_resource(RouteTable(
        "{}RouteTable".format(a),
        VpcId=Ref("VPC"),
        Tags=Tags(
            Name=Sub("${{AWS::StackName}} {}".format(a)),
        )
    ))
    t.add_resource(NetworkAcl(
        "{}NetworkAcl".format(a),
        VpcId=Ref("VPC"),
        Tags=Tags(
            Name=Sub("${{AWS::StackName}} {}".format(a))
        )
    ))
    for n in names:
        t.add_resource(Subnet(
            "{}Subnet{}".format(a, n),
            VpcId=Ref("VPC"),
            AvailabilityZone=Select(count % 4, GetAZs()),
            CidrBlock=Sub("10.${{ClassB}}.{}.0/20".format(count * 16)),
            MapPublicIpOnLaunch="true" if a == "Public" else "false",
            Tags=Tags(
                Name=Sub("${{AWS::StackName}} {} {}".format(a, n)),
            )
        ))
        count += 1
        t.add_resource(SubnetRouteTableAssociation(
            "{}Subnet{}RouteTableAssociation".format(a, n),
            SubnetId=Ref("{}Subnet{}".format(a, n)),
            RouteTableId=Ref("{}RouteTable".format(a)),
        ))
        t.add_resource(SubnetNetworkAclAssociation(
            "{}Subnet{}NetworkAclAssociation".format(a, n),
            SubnetId=Ref("{}Subnet{}".format(a, n)),
            NetworkAclId=Ref("{}NetworkAcl".format(a)),
        ))

directions = ["Inbound", "Outbound"]
for a in accessibility:
    for d in directions:
        t.add_resource(NetworkAclEntry(
            "{}{}NetworkAclEntry".format(d, a),
            NetworkAclId=Ref("{}NetworkAcl".format(a)),
            RuleNumber="100",
            Protocol="-1",
            Egress="true" if d == "Outbound" else "false",
            RuleAction="allow",
            CidrBlock="0.0.0.0/0",
        ))
t.add_resource(Route(
    "RouteTablePublicInternetRoute",
    GatewayId=Ref("InternetGateway"),
    DestinationCidrBlock="0.0.0.0/0",
    RouteTableId=Ref("PublicRouteTable"),
))

t.add_resource(EIP(
    "EIP",
    Domain="VPC"
))

t.add_resource(NatGateway(
    "NatGateway",
    AllocationId=GetAtt("EIP", "AllocationId"),
    SubnetId=Ref("PublicSubnetA")
))


t.add_resource(Route(
    "RouteNat",
    RouteTableId=Ref("PrivateRouteTable"),
    DestinationCidrBlock="0.0.0.0/0",
    NatGatewayId=Ref("NatGateway")
))

t.add_output(Output(
    "VPCId",
    Description="VPCId of the newly created VPC",
    Value=Ref("VPC"),
))

print(t.to_json())
