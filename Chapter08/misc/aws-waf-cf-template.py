#!/usr/bin/env python
"""Generating CloudFormation template."""

from troposphere import (
    Template,
    Parameter,
    Join,
    Ref
)
from troposphere.wafregional import (
    Rule,
    SqlInjectionMatchSet,
    WebACL,
    SizeConstraintSet,
    IPSet,
    XssMatchSet,
    Predicates,
    SqlInjectionMatchTuples,
    FieldToMatch,
    Action,
    Rules,
    SizeConstraint,
    XssMatchTuple,
    WebACLAssociation
)

t = Template()

t.add_version("2010-09-09")

t.add_description("Effective DevOps in AWS: AWS WAF against common attacks")

t.add_parameter(Parameter(
    "WebACLName",
    Default="CommonAttackProtection",
    Type="String",
    Description="Enter the name you want to use for the WebACL"
))

t.add_parameter(Parameter(
    "ALBArn",
    Type="String",
    Description="ALB Arn resource you want to protect",
))

t.add_resource(SqlInjectionMatchSet(
    "SqliMatchSet",
    Name=Join("", [Ref("WebACLName"), "SqliMatch"]),
    SqlInjectionMatchTuples=[
        SqlInjectionMatchTuples(
            FieldToMatch=FieldToMatch(Type="QUERY_STRING"),
            TextTransformation="URL_DECODE"
        ),
        SqlInjectionMatchTuples(
            FieldToMatch=FieldToMatch(Type="QUERY_STRING"),
            TextTransformation="HTML_ENTITY_DECODE"
        ),
        SqlInjectionMatchTuples(
            FieldToMatch=FieldToMatch(Type="BODY"),
            TextTransformation="URL_DECODE"
        ),
        SqlInjectionMatchTuples(
            FieldToMatch=FieldToMatch(Type="BODY"),
            TextTransformation="HTML_ENTITY_DECODE"
        ),
        SqlInjectionMatchTuples(
            FieldToMatch=FieldToMatch(Type="URI"),
            TextTransformation="URL_DECODE"
        )
    ]
))

t.add_resource(Rule(
    "SqliRule",
    Predicates=[
        Predicates(
            DataId=Ref("SqliMatchSet"),
            Type="SqlInjectionMatch",
            Negated=False
        )
    ],
    Name=Join("", [Ref("WebACLName"), "SqliRule"]),
    MetricName=Join("", [Ref("WebACLName"), "SqliRule"]),
))

t.add_resource(XssMatchSet(
    "XssMatchSet",
    Name=Join("", [Ref("WebACLName"), "XssMatch"]),
    XssMatchTuples=[
        XssMatchTuple(
            FieldToMatch=FieldToMatch(Type="QUERY_STRING"),
            TextTransformation="URL_DECODE"
        ),
        XssMatchTuple(
            FieldToMatch=FieldToMatch(Type="QUERY_STRING"),
            TextTransformation="HTML_ENTITY_DECODE"
        ),
        XssMatchTuple(
            FieldToMatch=FieldToMatch(Type="BODY"),
            TextTransformation="URL_DECODE"
        ),
        XssMatchTuple(
            FieldToMatch=FieldToMatch(Type="BODY"),
            TextTransformation="HTML_ENTITY_DECODE"
        ),
        XssMatchTuple(
            FieldToMatch=FieldToMatch(Type="URI"),
            TextTransformation="URL_DECODE"
        )
    ]
))

t.add_resource(Rule(
    "XssRule",
    Name=Join("", [Ref("WebACLName"), "XssRule"]),
    Predicates=[
        Predicates(
            DataId=Ref("XssMatchSet"),
            Type="XssMatch",
            Negated=False
        )
    ],
    MetricName=Join("", [Ref("WebACLName"), "XssRule"]),
))

t.add_resource(IPSet(
    "WAFManualIPBlockSet",
    Name="Manual IP Block Set",
))

t.add_resource(Rule(
    "ManualIPBlockRule",
    Name=Join("", [Ref("WebACLName"), "ManualIPBlockRule"]),
    MetricName=Join("", [Ref("WebACLName"), "ManualIPBlockRule"]),
    Predicates=[
        Predicates(
            DataId=Ref("WAFManualIPBlockSet"),
            Type="IPMatch",
            Negated=False
        )
    ]
))

t.add_resource(SizeConstraintSet(
    "SizeMatchSet",
    Name=Join("", [Ref("WebACLName"), "LargeBodyMatch"]),
    SizeConstraints=[
        SizeConstraint(
            ComparisonOperator="GT",
            TextTransformation="NONE",
            FieldToMatch=FieldToMatch(Type="BODY"),
            Size="8192"
        )
    ]
))

t.add_resource(Rule(
    "SizeMatchRule",
    Name=Join("", [Ref("WebACLName"), "LargeBodyMatchRule"]),
    MetricName=Join("", [Ref("WebACLName"), "DetectLargeBody"]),
    Predicates=[
        Predicates(
            DataId=Ref("SizeMatchSet"),
            Type="SizeConstraint",
            Negated=False
        )
    ]
))

t.add_resource(WebACL(
    "MyWebACL",
    Name=Ref("WebACLName"),
    DefaultAction=Action(Type="ALLOW"),
    Rules=[
        Rules(
            Action=Action(Type="BLOCK"),
            Priority=1,
            RuleId=Ref("ManualIPBlockRule")
        ),
        Rules(
            Action=Action(Type="COUNT"),
            Priority=2,
            RuleId=Ref("SizeMatchRule")
        ),
        Rules(
            Action=Action(Type="BLOCK"),
            Priority=3,
            RuleId=Ref("SqliRule")
        ),
        Rules(
            Action=Action(Type="BLOCK"),
            Priority=4,
            RuleId=Ref("XssRule")
        )
    ],
    MetricName=Ref("WebACLName"),
))

t.add_resource(WebACLAssociation(
    "WebACLAssociation",
    ResourceArn=Ref("ALBArn"),
    WebACLId=Ref("MyWebACL")
))

print(t.to_json())
