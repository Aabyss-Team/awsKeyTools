# -*- coding: utf-8 -*-
import json
import requests
import boto3
from botocore.exceptions import ClientError
import argparse
import urllib.parse
import logging
import re

"""Main module."""


def run(args: argparse.Namespace) -> str:
    """
    Takes the arguments from the CLI and generates the link
    :param args: the namespace from the CLI
    :type args: argparse.Namespace
    :return: sign-in URL
    """
    # Set up logging
    logger = logging.getLogger(__name__)

    # Set up the base session
    session: boto3.Session
    logger.debug("Establishing Boto3 session.")
    # If we have a profile, use that.
    if args.profile:
        logger.debug("Using CLI-provided profile.")
        session = boto3.Session(profile_name=args.profile,
                                region_name=args.region)
        logger.info("Profile session using \"%s\" established.", args.profile)
    # Otherwise, use the command line arguments
    elif args.access_key_id:
        logger.debug("Using CLI-provided credentials.")
        session = boto3.Session(aws_access_key_id=args.access_key_id,
                                aws_secret_access_key=args.secret_access_key,
                                aws_session_token=args.session_token,
                                region_name=args.region)
        logger.info("Session using credential variables established.")
    # Otherwise, let boto figure it out.
    else:
        logger.debug("No credentials detected, forwarding to Boto3.")
        session = boto3.Session(region_name=args.region)
        logger.info("Boto3 session established.")

    # Get to temporary credentials
    # If we have a role ARN supplied, start assuming them
    if args.role_arn:
        logger.debug("Role detected, setting up STS.")
        sts = session.client("sts", endpoint_url=args.sts_endpoint)
        logger.info("Assuming role \"%s\" via STS.", args.role_arn)
        resp = sts.assume_role(RoleArn=args.role_arn,
                               RoleSessionName="aws_consoler")
        creds = resp["Credentials"]
        logger.debug("Role assumed, setting up session.")
        session = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"])
        logger.info("New role session established.")
    # If we are still a permanent IAM credential, use sts:GetFederationToken
    elif session.get_credentials().get_frozen_credentials() \
            .access_key.startswith("AKIA"):
        sts = session.client("sts", endpoint_url=args.sts_endpoint)
        logger.warning("Creds still permanent, creating federated session.")
        # Effective access is calculated as the union of our permanent creds
        # and the policies supplied here. Use the AdministratorAccess policy
        # for the largest set of possible permissions.
        try:
            resp = sts.get_federation_token(
                Name="aws_consoler",
                PolicyArns=[
                    {"arn": "arn:aws:iam::aws:policy/AdministratorAccess"}
                ])
            logger.debug("Federation session created, setting up session.")
            creds = resp["Credentials"]
            session = boto3.Session(
                aws_access_key_id=creds["AccessKeyId"],
                aws_secret_access_key=creds["SecretAccessKey"],
                aws_session_token=creds["SessionToken"])
            logger.info("New federated session established.")
        except ClientError:
            message = "Error obtaining federation token from STS. Ensure " \
                      "the IAM user has sts:GetFederationToken permissions, " \
                      "or provide a role to assume. "
            raise PermissionError(message)

    # Check that our credentials are valid.
    sts = session.client("sts", endpoint_url=args.sts_endpoint)
    resp = sts.get_caller_identity()
    logger.info("Session valid, attempting to federate as %s.", resp["Arn"])

    # TODO: Detect things like user session credentials here.

    # Get the partition-specific URLs.
    partition_metadata = _get_partition_endpoints(session.region_name)
    federation_endpoint = args.federation_endpoint if args.federation_endpoint \
        else partition_metadata["federation"]
    console_endpoint = args.console_endpoint if args.console_endpoint\
        else partition_metadata["console"]

    # Generate our signin link, given our temporary creds
    creds = session.get_credentials().get_frozen_credentials()
    logger.debug("Session credentials frozen.")
    json_creds = json.dumps(
        {"sessionId": creds.access_key,
         "sessionKey": creds.secret_key,
         "sessionToken": creds.token})
    token_params = {
        "Action": "getSigninToken",
        # TODO: Customize duration for federation and sts:AssumeRole
        "SessionDuration": 43200,
        "Session": json_creds
    }
    logger.debug("Creating console federation token.")
    resp = requests.get(url=federation_endpoint, params=token_params)
    # Stacking AssumeRole sessions together will generate a 400 error here.
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError(
            "Couldn't obtain federation token (trying to stack roles?): "
            + str(e))

    fed_token = json.loads(resp.text)["SigninToken"]
    logger.debug("Federation token obtained, building URL.")
    console_params = {}
    if args.region:
        console_params["region"] = args.region
    login_params = {
        "Action": "login",
        "Issuer": "consoler.local",
        "Destination": console_endpoint + "?"
                       + urllib.parse.urlencode(console_params),
        "SigninToken": fed_token
    }
    login_url = federation_endpoint + "?" \
                + urllib.parse.urlencode(login_params)

    logger.info("URL generated!")
    return (login_url)


def _get_partition_endpoints(region: str):
    # TODO: Implement boto/botocore#1715 when merged
    logger = logging.getLogger(__name__)

    # AWS China endpoints
    if re.match(r"^cn-\w+-\d+$", region):
        logger.info("Using AWS China partition.")
        return {
            "partition": "aws-cn",
            "console": "https://console.amazonaws.cn/console/home",
            "federation": "https://signin.amazonaws.cn/federation",
        }

    # AWS GovCloud endpoints
    if re.match(r"^us-gov-\w+-\d+$", region):
        logger.info("Using AWS GovCloud partition.")
        return {
            "partition": "aws-us-gov",
            "console": "https://console.amazonaws-us-gov.com/console/home",
            "federation": "https://signin.amazonaws-us-gov.com/federation"
        }

    # AWS ISO endpoints (guessing from suffixes in botocore's endpoints.json)
    if re.match(r"^us-iso-\w+-\d+$", region):
        logger.warning("Using undocumented AWS ISO partition, guessing URLs!")
        return {
            "partition": "aws-iso",
            "console": "https://console.c2s.ic.gov/console/home",
            "federation": "https://signin.c2s.ic.gov/federation"
        }

    # AWS ISOB endpoints (see above)
    if re.match(r"^us-isob-\w+-\d+$", region):
        logger.warning("Using undocumented AWS ISOB partition, guessing URLs!")
        return {
            "partition": "aws-iso-b",
            "console": "https://console.sc2s.sgov.gov/console/home",
            "federation": "https://signin.sc2s.sgov.gov/federation"
        }

    # Otherwise, we (should?) be using the default partition.
    if re.match(r"^(us|eu|ap|sa|ca|me)-\w+-\d+$", region):
        pass
    else:
        logger.warning("Could not detect partition! Using AWS Standard. "
                       "If this is incorrect, consider using -eF and -eC.")
    return {
        "partition": "aws",
        "console": "https://console.aws.amazon.com/console/home",
        "federation": "https://signin.aws.amazon.com/federation"
    }
