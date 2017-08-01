"""Generating CloudFormation template."""

from troposphere import Join

from troposphere import (
    Ref,
    Template
)

from troposphere.s3 import Bucket

from troposphere.s3 import BucketPolicy

from troposphere.cloudtrail import Trail


t = Template()

t.add_description("Effective DevOps in AWS: Turn on CloudTrail and log to S3")

t.add_resource(Bucket(
    "S3Bucket",
    DeletionPolicy="Retain"
))

t.add_resource(BucketPolicy(
    "BucketPolicy",
    Bucket=Ref("S3Bucket"),
    PolicyDocument={
        "Statement": [{
            "Action": "s3:GetBucketAcl",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Resource": Join("", [
                "arn:aws:s3:::", Ref("S3Bucket")
            ])
        }, {
            "Action": "s3:PutObject",
            "Effect": "Allow",
            "Principal": {
                "Service": "cloudtrail.amazonaws.com"
            },
            "Resource": Join("", [
                "arn:aws:s3:::",
                Ref("S3Bucket"),
                "/AWSLogs/",
                Ref("AWS::AccountId"),
                "/*"
            ]),
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }]
    },
))

t.add_resource(Trail(
    "Trail",
    S3BucketName=Ref("S3Bucket"),
    IsLogging=True,
    EnableLogFileValidation=True,
    IncludeGlobalServiceEvents=True,
    IsMultiRegionTrail=True,
    DependsOn=["BucketPolicy"]
))

print(t.to_json())
