"""Generating CloudFormation template."""

from troposphere import elasticloadbalancingv2 as elb

from troposphere import (
    Export,
    GetAtt,
    ImportValue,
    Join,
    Output,
    Ref,
    Select,
    Split,
    Sub,
    Template,
    ec2
)

from awacs.aws import Allow, Policy, Principal, Statement

from awacs.s3 import PutObject, ARN

from troposphere.s3 import (
    Bucket,
    BucketPolicy,
)

from troposphere.cloudwatch import (
    Alarm,
    MetricDimension,
)

t = Template()

t.add_description("Effective DevOps in AWS: ALB for the ECS Cluster")

t.add_resource(Bucket(
    "S3Bucket",
    DeletionPolicy="Retain",
))

t.add_resource(BucketPolicy(
    'BucketPolicy',
    Bucket=Ref("S3Bucket"),
    PolicyDocument=Policy(
        Version='2012-10-17',
        Statement=[
            Statement(
                Action=[PutObject],
                Effect=Allow,
                Principal=Principal("AWS", ["127311923021"]),
                Resource=[Join('',
                               [ARN(''),
                                Ref("S3Bucket"),
                                   "/AWSLogs/511912822958/*"])],
            )
        ]
    )
))


t.add_resource(ec2.SecurityGroup(
    "LoadBalancerSecurityGroup",
    GroupDescription="Web load balancer security group.",
    VpcId=ImportValue(
        Join(
            "-",
            [Select(0, Split("-", Ref("AWS::StackName"))),
                "cluster-vpc-id"]
        )
    ),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="3000",
            ToPort="3000",
            CidrIp="0.0.0.0/0",
        ),
    ],
))

t.add_resource(elb.LoadBalancer(
    "LoadBalancer",
    Scheme="internet-facing",
    Subnets=Split(
        ',',
        ImportValue(
            Join("-",
                 [Select(0, Split("-", Ref("AWS::StackName"))),
                  "cluster-public-subnets"]
                 )
        )
    ),
    SecurityGroups=[Ref("LoadBalancerSecurityGroup")],
    LoadBalancerAttributes=[
        elb.LoadBalancerAttributes(
            Key="access_logs.s3.enabled",
            Value="true",
        ),
        elb.LoadBalancerAttributes(
            Key="access_logs.s3.bucket",
            Value=Ref("S3Bucket"),
        )
    ],
))

t.add_resource(elb.TargetGroup(
    "TargetGroup",
    DependsOn='LoadBalancer',
    HealthCheckIntervalSeconds="20",
    HealthCheckProtocol="HTTP",
    HealthCheckTimeoutSeconds="15",
    HealthyThresholdCount="5",
    Matcher=elb.Matcher(
        HttpCode="200"),
    Port=3000,
    Protocol="HTTP",
    UnhealthyThresholdCount="3",
    VpcId=ImportValue(
        Join(
            "-",
            [Select(0, Split("-", Ref("AWS::StackName"))),
                "cluster-vpc-id"]
        )
    ),
))

t.add_resource(elb.Listener(
    "Listener",
    Port="3000",
    Protocol="HTTP",
    LoadBalancerArn=Ref("LoadBalancer"),
    DefaultActions=[elb.Action(
        Type="forward",
        TargetGroupArn=Ref("TargetGroup")
    )]
))

t.add_output(Output(
    "TargetGroup",
    Description="TargetGroup",
    Value=Ref("TargetGroup"),
    Export=Export(Sub("${AWS::StackName}-target-group")),
))

t.add_output(Output(
    "URL",
    Description="Helloworld URL",
    Value=Join("", ["http://", GetAtt("LoadBalancer", "DNSName"), ":3000"])
))


t.add_resource(Alarm(
    "ELBHTTP5xxs",
    AlarmDescription="Alarm if HTTP 5xxs too high",
    Namespace="AWS/ELB",
    MetricName="HTTPCode_Backend_5XX",
    Dimensions=[
        MetricDimension(
            Name="LoadBalancerName",
            Value=Ref("LoadBalancer")
        ),
    ],
    Statistic="Average",
    Period="60",
    EvaluationPeriods="3",
    Threshold="30",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    AlarmActions=["arn:aws:sns:us-east-1:511912822958:alert-sms"],
    OKActions=["arn:aws:sns:us-east-1:511912822958:alert-sms"],
    InsufficientDataActions=[],
))

t.add_resource(Alarm(
    "ELBHLatency",
    AlarmDescription="Alarm if Latency too high",
    Namespace="AWS/ELB",
    MetricName="Latency",
    Dimensions=[
        MetricDimension(
            Name="LoadBalancerName",
            Value=Ref("LoadBalancer")
        ),
    ],
    Statistic="Average",
    Period="60",
    EvaluationPeriods="5",
    Threshold="0.5",
    ComparisonOperator="GreaterThanOrEqualToThreshold",
    AlarmActions=["arn:aws:sns:us-east-1:511912822958:alert-sms"],
    OKActions=["arn:aws:sns:us-east-1:511912822958:alert-sms"],
    InsufficientDataActions=[],
))
print(t.to_json())
