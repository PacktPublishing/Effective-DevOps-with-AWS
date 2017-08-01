"""Generating CloudFormation template."""

from ipaddress import ip_network

from ipify import get_ip

from troposphere import (
    GetAtt,
    Join,
    Output,
    Export,
    Parameter,
    Ref,
    Template,
)

from troposphere.elasticsearch import (
    Domain,
    EBSOptions,
    ElasticsearchClusterConfig,
)

t = Template()

PublicCidrIp = str(ip_network(get_ip()))

t.add_description('Effective DevOps in AWS: Elasticsearch')

t.add_parameter(Parameter(
    "InstanceType",
    Type="String",
    Description="instance type",
    Default="t2.small.elasticsearch",
    AllowedValues=[
        "t2.small.elasticsearch",
        "t2.medium.elasticsearch",
        "m4.large.elasticsearch",
    ],
))

t.add_parameter(Parameter(
    "InstanceCount",
    Default="2",
    Type="String",
    Description="Number instances in the cluster",
))

t.add_parameter(Parameter(
    "VolumeSize",
    Default="10",
    Type="String",
    Description="Size in Gib of the EBS volumes",
))

t.add_resource(Domain(
    'ElasticsearchCluster',
    DomainName="logs",
    ElasticsearchVersion="5.3",
    ElasticsearchClusterConfig=ElasticsearchClusterConfig(
        DedicatedMasterEnabled=False,
        InstanceCount=Ref("InstanceCount"),
        ZoneAwarenessEnabled=False,
        InstanceType=Ref("InstanceType"),
    ),
    AdvancedOptions={
        "indices.fielddata.cache.size": "",
        "rest.action.multi.allow_explicit_index": "true",
    },
    EBSOptions=EBSOptions(EBSEnabled=True,
                          Iops=0,
                          VolumeSize=Ref("VolumeSize"),
                          VolumeType="gp2"),
    AccessPolicies={
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Principal': {
                    'AWS': [Ref('AWS::AccountId')]
                },
                'Action': 'es:*',
                'Resource': '*',
            },
            {
                'Effect': 'Allow',
                'Principal': {
                    'AWS': "*"
                },
                'Action': 'es:*',
                'Resource': '*',
                'Condition': {
                    'IpAddress': {
                        'aws:SourceIp': PublicCidrIp
                    }
                }

            }
        ]
    },
))

t.add_output(Output(
    "DomainArn",
    Description="Domain Arn",
    Value=GetAtt("ElasticsearchCluster", "DomainArn"),
    Export=Export("LogsDomainArn"),
))

t.add_output(Output(
    "Kibana",
    Description="Kibana url",
    Value=Join("", [
        "https://",
        GetAtt("ElasticsearchCluster", "DomainEndpoint"),
        "/_plugin/kibana/"
    ])
))

print t.to_json()
