"""Generating CloudFormation template."""

from troposphere import (
    Template,
    Join,
    Ref,
)

from troposphere.iam import (
    Group,
    ManagedPolicy,
)

from awacs.aws import (
    Action,
    Allow,
    Condition,
    NumericGreaterThan,
    Deny,
    Null,
    Policy,
    Statement,
)

t = Template()

t.add_description("Effective DevOps in AWS: User Groups")

t.add_resource(Group(
    "Admins",
    GroupName="Admins",
    ManagedPolicyArns=[
        "arn:aws:iam::aws:policy/AdministratorAccess"
    ],
))

t.add_resource(ManagedPolicy(
    "CommonIamPolicy",
    Description="Common policy to manage IAM resources",
    PolicyDocument=Policy(
        Version="2012-10-17",
        Statement=[
            Statement(
                Effect=Allow,
                Action=[
                    Action("iam", "GetAccountPasswordPolicy"),
                    Action("iam", "ListUsers"),
                    Action("iam", "ListMFADevices"),
                    Action("iam", "ListVirtualMFADEvices")
                ],
                Resource=["*"]
            ),
            Statement(
                Effect=Allow,
                Action=[
                    Action("iam", "CreateVirtualMFADevice")
                ],
                Resource=[
                    Join(
                        "",
                        [
                            "arn:aws:iam::",
                            Ref("AWS::AccountId"),
                            ":mfa/${aws:username}",
                        ]
                    )
                ]
            ),
            Statement(
                Effect=Allow,
                Action=[
                    Action("iam", "ChangePassword"),
                    Action("iam", "CreateAccessKey"),
                    Action("iam", "CreateLoginProfile"),
                    Action("iam", "DeleteAccessKey"),
                    Action("iam", "DeleteLoginProfile"),
                    Action("iam", "EnableMFADevice"),
                    Action("iam", "GetAccessKeyLastUsed"),
                    Action("iam", "GetLoginProfile"),
                    Action("iam", "GetUser"),
                    Action("iam", "ListAccessKeys"),
                    Action("iam", "UpdateAccessKey"),
                    Action("iam", "UpdateLoginProfile")
                ],
                Resource=[
                    Join(
                        "",
                        [
                            "arn:aws:iam::",
                            Ref("AWS::AccountId"),
                            ":user/${aws:username}",
                        ]
                    )
                ]
            ),
            Statement(
                Effect=Deny,
                NotAction=[
                    Action("iam", "ChangePassword"),
                    Action("iam", "CreateVirtualMFADevice"),
                    Action("iam", "EnableMFADevice"),
                    Action("iam", "GetUser"),
                    Action("iam", "ListMFADevices"),
                    Action("iam", "ListUsers"),
                    Action("iam", "ListVirtualMFADEvices")
                ],
                Resource=["*"],
                Condition=Condition(
                    Null("aws:MultiFactorAuthAge", "true"),
                ),
            ),
            Statement(
                Effect=Deny,
                NotAction=[
                    Action("iam", "ChangePassword"),
                    Action("iam", "CreateVirtualMFADevice"),
                    Action("iam", "EnableMFADevice"),
                    Action("iam", "GetUser"),
                    Action("iam", "ListMFADevices"),
                    Action("iam", "ListUsers"),
                    Action("iam", "ListVirtualMFADEvices")
                ],
                Resource=["*"],
                Condition=Condition(
                    NumericGreaterThan("aws:MultiFactorAuthAge", "43200")
                ),
            ),
        ]
    )
))

t.add_resource(Group(
    "AllUsers",
    GroupName="AllUsers",
    ManagedPolicyArns=[
        Ref("CommonIamPolicy")
    ]
))

print t.to_json()
