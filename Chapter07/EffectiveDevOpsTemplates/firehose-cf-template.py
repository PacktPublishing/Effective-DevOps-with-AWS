"""Generating CloudFormation template."""

from troposphere import (
    GetAtt,
    Join,
    Ref,
    Template,
    ImportValue
)

from troposphere.firehose import (
    BufferingHints,
    CloudWatchLoggingOptions,
    DeliveryStream,
    S3Configuration,
    ElasticsearchDestinationConfiguration,
    RetryOptions,
)

from troposphere.iam import Role

from troposphere.s3 import Bucket

t = Template()

t.add_description('Effective DevOps in AWS: Kinesis Firehose Stream')


t.add_resource(Bucket(
    "S3Bucket",
    DeletionPolicy="Retain"
))

t.add_resource(Role(
    'FirehoseRole',
    ManagedPolicyArns=[
        'arn:aws:iam::aws:policy/AmazonS3FullAccess',
        'arn:aws:iam::aws:policy/AmazonESFullAccess',
    ],
    AssumeRolePolicyDocument={
        'Version': '2012-10-17',
        'Statement': [{
            'Action': 'sts:AssumeRole',
            'Principal': {'Service': 'firehose.amazonaws.com'},
            'Effect': 'Allow',
        }]
    }
))

t.add_resource(DeliveryStream(
    'FirehoseLogs',
    DeliveryStreamName='FirehoseLogs',
    ElasticsearchDestinationConfiguration=ElasticsearchDestinationConfiguration(
        DomainARN=ImportValue("LogsDomainArn"),
        RoleARN=GetAtt("FirehoseRole", "Arn"),
        IndexName="logs",
        TypeName="Logs",
        IndexRotationPeriod="OneDay",
        RetryOptions=RetryOptions(
            DurationInSeconds="300"
        ),
        BufferingHints=BufferingHints(
            IntervalInSeconds=60,
            SizeInMBs=1
        ),
        S3BackupMode="AllDocuments",
        S3Configuration=S3Configuration(
            BufferingHints=BufferingHints(
                IntervalInSeconds=300,
                SizeInMBs=5
            ),
            BucketARN=Join("", [
                "arn:aws:s3:::", Ref("S3Bucket")
            ]),
            CompressionFormat='UNCOMPRESSED',
            Prefix='firehose-logs',
            RoleARN=GetAtt("FirehoseRole", "Arn"),
        ),
    )
))

print t.to_json()
