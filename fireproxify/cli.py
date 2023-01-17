import argparse
import sys
from typing import Tuple

from fireproxify.fireproxify import (
    AWS_DEFAULT_REGIONS,
    FireProx,
    FireProxException,
    parse_region,
)


def parse_arguments() -> Tuple[argparse.Namespace, str]:
    """Parse command line arguments and return namespace

    :return: Namespace for arguments and help text as a tuple
    """
    parser = argparse.ArgumentParser(description="FireProx API Gateway Manager")
    parser.add_argument("--profile_name", help="AWS Profile Name to store/retrieve credentials", type=str, default=None)
    parser.add_argument("--access_key", help="AWS Access Key", type=str, default=None)
    parser.add_argument("--secret_access_key", help="AWS Secret Access Key", type=str, default=None)
    parser.add_argument("--session_token", help="AWS Session Token", type=str, default=None)
    parser.add_argument(
        "--region",
        help="AWS Regions (accepts single region, comma-separated list of regions or file containing regions)",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--command", help="Commands: list, list_all, create, delete, prune, update", type=str, default=None
    )
    parser.add_argument("--api_id", help="API ID", type=str, required=False)
    parser.add_argument("--url", help="URL end-point", type=str, required=False)
    return parser.parse_args(), parser.format_help()


def do_list(args):
    region_parsed = parse_region(args.region)
    if isinstance(region_parsed, list):
        for region in region_parsed:
            args.region = region
            fp = FireProx(**vars(args))
            print(f"Listing API's from {fp.region}...")
            results = fp.list_api(deleting=False)
            for result in results:
                print(result)
    else:
        args.region = region_parsed
        fp = FireProx(**vars(args))
        print(f"Listing API's from {fp.region}...")
        results = fp.list_api(deleting=False)
        for result in results:
            print(result)


def do_list_all(args):
    for region in AWS_DEFAULT_REGIONS:
        args.region = region
        fp = FireProx(**vars(args))
        print(f"Listing API's from {fp.region}...")
        results = fp.list_api(deleting=False)
        for result in results:
            print(result)


def do_create(args):
    if not args.url:
        raise FireProxException("Please provide a valid URL end-point")
    region_parsed = parse_region(args.region, mode="random")
    args.region = region_parsed
    print(f"Creating => {args.url}...")
    fp = FireProx(**vars(args))
    _, result = fp.create_api(args.url)
    print(result)


def do_delete(args):
    if not args.api_id:
        raise FireProxException("Please provide a valid API id")
    region_parsed = parse_region(args.region)
    if region_parsed is None or isinstance(region_parsed, str):
        args.region = region_parsed
        fp = FireProx(**vars(args))
        result, msg = fp.delete_api(args.api_id)
        if result:
            print(f"Deleting {args.api_id} => Success!")
        else:
            print(f"Deleting {args.api_id} => Failed! ({msg})")
    else:
        raise FireProxException("[ERROR] More than one region provided for command 'delete'\n")


def do_prune(args):
    region_parsed = parse_region(args.region)
    if region_parsed is None:
        region_parsed = AWS_DEFAULT_REGIONS
    if isinstance(region_parsed, str):
        region_parsed = [region_parsed]
    while True:
        choice = input(f"This will delete ALL APIs from region(s): {','.join(region_parsed)}. Proceed? [y/N] ") or "N"
        if choice.upper() in ["Y", "N"]:
            break
    if choice.upper() == "Y":
        for region in region_parsed:
            args.region = region
            fp = FireProx(**vars(args))
            print(f"Retrieving API's from {region}...")
            current_apis = fp.list_api(deleting=True)
            if len(current_apis) == 0:
                print("No API found")
            else:
                for api in current_apis:
                    result, msg = fp.delete_api(api_id=api["id"])
                    if result:
                        print(f'Deleting {api["id"]} => Success!')
                    else:
                        print(f'Deleting {api["id"]} => Failed! ({msg})')


def do_update(args):
    if not args.api_id:
        raise FireProxException("Please provide a valid API id")
    if not args.url:
        raise FireProxException("Please provide a valid URL end-point")
    region_parsed = parse_region(args.region)
    if isinstance(region_parsed, list):
        raise FireProxException("[ERROR] More than one region provided for command 'update'\n")
    fp = FireProx(**vars(args))
    print(f"Updating {args.api_id} => {args.url}...")
    result = fp.update_api(args.api_id, args.url)
    success = "Success!" if result else "Failed!"
    print(f"API Update Complete: {success}")


def cli_main():
    """Run the main program

    :return:
    """
    args, help_text = parse_arguments()

    try:
        if not args.command:
            raise FireProxException("Please provide a valid command")

        if args.command == "list":
            do_list(args)

        elif args.command == "list_all":
            do_list_all(args)

        elif args.command == "create":
            do_create(args)

        elif args.command == "delete":
            do_delete(args)

        elif args.command == "prune":
            do_prune(args)

        elif args.command == "update":
            do_update(args)

        else:
            raise FireProxException(f"[ERROR] Unsupported command: {args.command}\n")

    except FireProxException:
        print(help_text)
        sys.exit(1)
