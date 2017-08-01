"""Generating CloudFormation template."""

from troposphere import (
    ec2,
    GetAtt,
    Output,
    Parameter,
    Ref,
    Template,
    Select,
)

t = Template()

t.add_description("Effective DevOps in AWS: SoftEtherVPN Server")

t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2KeyPair."
))

t.add_parameter(Parameter(
    "VpcId",
    Type="AWS::EC2::VPC::Id",
    Description="VPC"
))

t.add_parameter(Parameter(
    "PublicSubnet",
    Description="PublicSubnet",
    Type="List<AWS::EC2::Subnet::Id>",
    ConstraintDescription="PublicSubnet"
))

t.add_resource(ec2.SecurityGroup(
    "VPNSecurityGroup",
    GroupDescription="SoftEther security group",
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="udp",
            FromPort="4500",
            ToPort="4500",
            CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="udp",
            FromPort="500",
            ToPort="500",
            CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="443",
            ToPort="443",
            CidrIp="0.0.0.0/0",
        )
    ],
    VpcId=Ref("VpcId")
))

t.add_resource(ec2.Instance(
    "server",
    ImageId="ami-a4c7edb2",
    InstanceType="t2.micro",
    KeyName=Ref("KeyPair"),
    NetworkInterfaces=[
        ec2.NetworkInterfaceProperty(
            GroupSet=[Ref("VPNSecurityGroup")],
            AssociatePublicIpAddress='true',
            SubnetId=Select("0", Ref("PublicSubnet")),
            DeviceIndex='0',
        )]
))

t.add_output(Output(
    "VPNAddress",
    Description="VPN address",
    Value=GetAtt("server", "PublicIp")
))

t.add_output(Output(
    "VPNUser",
    Description="VPN username",
    Value="vpn"
))

t.add_output(Output(
    "VPNPassword",
    Description="VPN password",
    Value=Ref("server")
))

t.add_output(Output(
    "VPNL2TP",
    Description="L2TPpreshared key for authentication",
    Value=Ref("server")
))

t.add_output(Output(
    "VPNAdminPassword",
    Description="Password to connect administration mode",
    Value=Ref("server")
))

print t.to_json()
