# -*- coding: utf-8 -*-

"""Console script for aws_consoler."""
import argparse
import sys
import webbrowser
import logging
from requests.exceptions import HTTPError

from aws_consoler.logic import run

LOG_FORMAT = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"


def main(argv=sys.argv[1:]):
    """Console script for aws_consoler.
    :return: shell exit code
    """

    # Set up logging
    logging.basicConfig(
        level=logging.WARNING,
        format=LOG_FORMAT
    )
    logger = logging.getLogger("aws_consoler.cli")

    # Set up parser
    logger.info("Setting up parser...")
    parser = argparse.ArgumentParser(
        description="A tool to generate an AWS console sign-in link from API "
                    "credentials using the federation endpoint.",
        # TODO: Add link to blog post
        # epilog="Read more about the generation of this tool at XXX"
    )

    # Add arguments
    logger.info("Adding parser argument groups...")
    profile_grp = parser.add_argument_group(title="Profile authentication")
    profile_grp.add_argument(
        "-p", "--profile",
        help="The profile to use for generating the link. Uses named "
             "profiles from the AWS CLI, as well as other Boto3 "
             "applications. Instructions available here: "
             "https://amzn.to/34ik2v7")
    logger.debug("Profile group ready.")

    creds_grp = parser.add_argument_group(title="Credential authentication")
    creds_grp.add_argument(
        "-a", "--access-key-id",
        help="The AWS access key ID to use for authentication. Should start "
             "with 'AKIA' or 'ASIA', depending on the credential type in use "
             "(permanent/temporary).")
    creds_grp.add_argument(
        "-s", "--secret-access-key",
        help="The AWS secret access key to use for authentication.")
    creds_grp.add_argument(
        "-t", "--session-token",
        help="The AWS session token to use for authentication. Generally "
             "required when using temporary credentials.")
    logger.debug("Creds group ready.")

    gen_grp = parser.add_argument_group(title="General arguments")
    gen_grp.add_argument(
        "-r", "--role-arn",
        help="The role to assume for console access, if needed.")
    gen_grp.add_argument(
        "-R", "--region", default=None,
        help="The AWS region you'd like the console link to refer to. "
             "If using -p, overrides the default region of the profile. ")
    gen_grp.add_argument(
        "-o", "--open", action="store_true",
        help="Open the generated link in your system's default browser.")
    gen_grp.add_argument(
        "-v", "--verbose", action="count",
        help="Verbosity, repeat for more verbose output (up to 3)")
    logger.debug("General group ready.")

    adv_grp = parser.add_argument_group(title="Advanced arguments")
    adv_grp.add_argument(
        "-eS", "--sts-endpoint", default=None,
        help="[advanced] The endpoint for connecting to STS, if connecting "
             "from behind a corporate proxy or an unknown partition. Expects "
             "a URL with a trailing slash. Overrides the URL based on -R."
    )
    adv_grp.add_argument(
        "-eF", "--federation-endpoint",
        help="[advanced] The endpoint for console federation, if connecting "
             "from behind a corporate proxy or an unknown partition. Expects "
             "a URL to send federation requests to."
    )
    adv_grp.add_argument(
        "-eC", "--console-endpoint",
        help="[advanced] The URL for console access, if connecting"
             "from behind a corporate proxy or an unknown partition. Expects "
             "a URL to forward the user to after obtaining their federation "
             "token."
    )
    logger.debug("Advanced group ready.")

    logger.info("Parsing arguments...")
    if argv:
        args = parser.parse_args(argv)
    else:
        args = parser.parse_args([])
    args_dict = vars(args)
    logger.debug("Arguments matrix: %s",
                 str({k: bool(v) for k, v in args_dict.items()}))

    # Set up verbosity
    if args.verbose:
        cli_logger = logger
        logic_logger = logging.getLogger("aws_consoler.logic")
        if args.verbose == 1:
            cli_logger.setLevel(logging.INFO)
            logic_logger.setLevel(logging.INFO)
        if args.verbose >= 2:
            cli_logger.setLevel(logging.DEBUG)
            logic_logger.setLevel(logging.DEBUG)
        if args.verbose >= 3:
            logging.getLogger("boto3").setLevel(logging.DEBUG)
            logging.getLogger("botocore").setLevel(logging.DEBUG)
            logging.getLogger("urllib3").setLevel(logging.DEBUG)

    # Validate that we have good arguments
    # We should not have both a profile and credentials
    logger.info("Validating arguments...")
    if args.profile and (args.access_key_id or args.secret_access_key or
                         args.session_token):
        parser.error("Profile cannot be combined with credential arguments.")
    # If we have a session token, we need an access key ID + secret access key
    if args.session_token and not (args.access_key_id and
                                   args.secret_access_key):
        parser.error("Session token must also have an access key ID/secret "
                     "access key.")
    # If we have an access key ID or secret access key, we also need the other
    if bool(args.secret_access_key) != bool(args.access_key_id):
        parser.error("Access key ID and secret access key must be provided "
                     "together.")

    # Arguments are valid, call our logic
    try:
        logger.info("Calling logic.")
        url = run(args)
        if args.open:
            logger.info("Opening browser.")
            webbrowser.open(url, new=2)
        else:
            print(url)
    except PermissionError as e:
        logger.critical(e)
        exit(13)  # EACCES
    except HTTPError as e:
        logger.critical(e)
        exit(13)  # EACCES
    except Exception as e:
        # TODO: better exception handling
        logger.critical(e)
        exit(1)


if __name__ == "__main__":
    print(sys.argv)
    sys.exit(main(sys.argv[1:]))  # pragma: no cover
