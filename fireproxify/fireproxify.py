import configparser
import datetime
import os
import random
from time import sleep
from typing import List, Union

import boto3
import botocore
import tldextract


class FireProxException(Exception):
    pass


AWS_DEFAULT_REGIONS = [
    "ap-south-1",
    "eu-north-1",
    "eu-west-3",
    "eu-west-2",
    "eu-west-1",
    "ap-northeast-3",
    "ap-northeast-2",
    "ap-northeast-1",
    "ca-central-1",
    "sa-east-1",
    "ap-southeast-1",
    "ap-southeast-2",
    "eu-central-1",
    "us-east-1",
    "us-east-2",
    "us-west-1",
    "us-west-2",
]


class FireProx:
    def __init__(self, **kwargs):
        self.profile_name = None
        self.access_key = None
        self.secret_access_key = None
        self.session_token = None
        self.region = None
        self.api_list = []
        self.client = None
        self.__dict__.update(kwargs)

        if self.access_key and self.secret_access_key and not self.region:
            self.error("Please provide a region with AWS credentials")

        if not self.load_creds():
            self.error("Unable to load AWS credentials")

    def __str__(self):
        return "FireProx()"

    def _try_instance_profile(self) -> bool:
        """Try instance profile credentials

        :return:
        """
        try:
            if not self.region:
                self.client = boto3.client("apigateway")
            else:
                self.client = boto3.client("apigateway", region_name=self.region)
            self.client.get_account()
            self.region = self.client._client_config.region_name
            return True
        except BaseException:
            return False

    def _save_profile(self, config, config_profile_section, credentials):
        if config_profile_section not in config:
            config.add_section(config_profile_section)
        config[config_profile_section]["region"] = self.region
        with open(os.path.expanduser("~/.aws/config"), "w") as file:
            config.write(file)
        if self.profile_name not in credentials:
            credentials.add_section(self.profile_name)
        credentials[self.profile_name]["aws_access_key_id"] = self.access_key
        credentials[self.profile_name]["aws_secret_access_key"] = self.secret_access_key
        if self.session_token:
            credentials[self.profile_name]["aws_session_token"] = self.session_token
        else:
            credentials.remove_option(self.profile_name, "aws_session_token")
        with open(os.path.expanduser("~/.aws/credentials"), "w") as file:
            credentials.write(file)

    def load_creds(self) -> bool:
        """Load credentials from AWS config and credentials files if present.

        :return:
        """
        # If no access_key, secret_key, or profile name provided, try instance credentials
        if not any([self.access_key, self.secret_access_key, self.profile_name]):
            return self._try_instance_profile()
        # Read in AWS config/credentials files if they exist
        credentials = configparser.ConfigParser()
        credentials.read(os.path.expanduser("~/.aws/credentials"))
        config = configparser.ConfigParser()
        config.read(os.path.expanduser("~/.aws/config"))
        # If profile in files, try it, but flow through if it does not work
        config_profile_section = f"profile {self.profile_name}"
        if self.profile_name in credentials and self._load_creds_from_profile(config, config_profile_section):
            return True
        # Maybe had profile, maybe didn't
        if self.access_key and self.secret_access_key:
            return self._load_creds_from_secret(config, config_profile_section, credentials)

    def _load_creds_from_profile(self, config, config_profile_section) -> bool:
        if config_profile_section not in config and self.region is None:
            self.error(f"Please create a section for {self.profile_name} in your ~/.aws/config file or provide region")
        # if region is not set, load it from config
        if self.region is None:
            self.region = config[config_profile_section].get("region", "us-east-1")
        try:
            self.client = boto3.session.Session(profile_name=self.profile_name, region_name=self.region).client(
                "apigateway"
            )
            self.client.get_account()
            return True
        except BaseException:
            pass
        return False

    def _load_creds_from_secret(self, config, config_profile_section, credentials) -> bool:
        try:
            self.client = boto3.client(
                "apigateway",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_access_key,
                aws_session_token=self.session_token,
                region_name=self.region,
            )
            self.client.get_account()
            if self.region is None:
                self.region = self.client._client_config.region_name
            # Save/overwrite config if profile specified
            if self.profile_name:
                self._save_profile(config, config_profile_section, credentials)
            return True
        except BaseException:
            return False

    def error(self, error):
        raise FireProxException(error)

    def get_template(self, url):
        if url[-1] == "/":
            url = url[:-1]

        title = "fireprox_{}".format(tldextract.extract(url).domain)
        version_date = f"{datetime.datetime.now():%Y-%m-%dT%XZ}"
        template = """
        {
          "swagger": "2.0",
          "info": {
            "version": "{{version_date}}",
            "title": "{{title}}"
          },
          "basePath": "/",
          "schemes": [
            "https"
          ],
          "paths": {
            "/": {
              "get": {
                "parameters": [
                  {
                    "name": "proxy",
                    "in": "path",
                    "required": true,
                    "type": "string"
                  },
                  {
                    "name": "X-My-X-Forwarded-For",
                    "in": "header",
                    "required": false,
                    "type": "string"
                  }
                ],
                "responses": {},
                "x-amazon-apigateway-integration": {
                  "uri": "{{url}}/",
                  "responses": {
                    "default": {
                      "statusCode": "200"
                    }
                  },
                  "requestParameters": {
                    "integration.request.path.proxy": "method.request.path.proxy",
                    "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
                  },
                  "passthroughBehavior": "when_no_match",
                  "httpMethod": "ANY",
                  "cacheNamespace": "irx7tm",
                  "cacheKeyParameters": [
                    "method.request.path.proxy"
                  ],
                  "type": "http_proxy"
                }
              }
            },
            "/{proxy+}": {
              "x-amazon-apigateway-any-method": {
                "produces": [
                  "application/json"
                ],
                "parameters": [
                  {
                    "name": "proxy",
                    "in": "path",
                    "required": true,
                    "type": "string"
                  },
                  {
                    "name": "X-My-X-Forwarded-For",
                    "in": "header",
                    "required": false,
                    "type": "string"
                  }
                ],
                "responses": {},
                "x-amazon-apigateway-integration": {
                  "uri": "{{url}}/{proxy}",
                  "responses": {
                    "default": {
                      "statusCode": "200"
                    }
                  },
                  "requestParameters": {
                    "integration.request.path.proxy": "method.request.path.proxy",
                    "integration.request.header.X-Forwarded-For": "method.request.header.X-My-X-Forwarded-For"
                  },
                  "passthroughBehavior": "when_no_match",
                  "httpMethod": "ANY",
                  "cacheNamespace": "irx7tm",
                  "cacheKeyParameters": [
                    "method.request.path.proxy"
                  ],
                  "type": "http_proxy"
                }
              }
            }
          }
        }
        """
        template = template.replace("{{url}}", url)
        template = template.replace("{{title}}", title)
        template = template.replace("{{version_date}}", version_date)

        return str.encode(template)

    def create_api(self, url):
        if not url:
            self.error("Please provide a valid URL end-point")

        template = self.get_template(url)
        response = self.client.import_rest_api(parameters={"endpointConfigurationTypes": "REGIONAL"}, body=template)
        resource_id, proxy_url = self.create_deployment(response["id"])
        result = {"id": response["id"], "proxy_url": proxy_url}
        return result, self.store_api(
            response["id"], response["name"], response["createdDate"], response["version"], url, resource_id, proxy_url
        )

    def update_api(self, api_id, url):
        if not any([api_id, url]):
            self.error("Please provide a valid API ID and URL end-point")

        if url[-1] == "/":
            url = url[:-1]

        resource_id = self.get_resource(api_id)
        if resource_id:
            response = self.client.update_integration(
                restApiId=api_id,
                resourceId=resource_id,
                httpMethod="ANY",
                patchOperations=[
                    {
                        "op": "replace",
                        "path": "/uri",
                        "value": "{}/{}".format(url, r"{proxy}"),
                    },
                ],
            )
            return response["uri"].replace("/{proxy}", "") == url
        else:
            self.error(f"Unable to update, no valid resource for {api_id}")

    def delete_api(self, api_id):
        if not api_id:
            self.error("Please provide a valid API ID")
        retry = 3
        sleep_time = 3
        success = False
        error_msg = "Generic error"
        while retry > 0 and not success:
            try:
                self.client.delete_rest_api(restApiId=api_id)
            except botocore.exceptions.ClientError as err:
                if err.response["Error"]["Code"] == "NotFoundException":
                    error_msg = "API not found"
                    break
                elif err.response["Error"]["Code"] == "TooManyRequestsException":
                    error_msg = "Too many requests"
                    sleep(sleep_time)
                    sleep_time *= 2
                else:
                    error_msg = err.response["Error"]["Message"]
            except BaseException:
                error_msg = "Generic error"
            else:
                success = True
                error_msg = ""
            finally:
                retry -= 1
        return success, error_msg

    def list_api(self, deleted_api_id=None, deleting=False):
        results = []
        response = self.client.get_rest_apis()
        if deleting:
            return response["items"]
        for item in response["items"]:
            try:
                created_dt = item["createdDate"]
                api_id = item["id"]
                name = item["name"]
                proxy_url = self.get_integration(api_id).replace("{proxy}", "")
                url = f"https://{api_id}.execute-api.{self.region}.amazonaws.com/fireprox/"
                if api_id != deleted_api_id:
                    results.append(f"[{created_dt}] ({api_id}) {name}: {url} => {proxy_url}")
            except BaseException:
                pass

        return results

    def store_api(self, api_id, name, created_dt, version_dt, url, resource_id, proxy_url):
        return f"[{created_dt}] ({api_id}) {name} => {proxy_url} ({url})"

    def create_deployment(self, api_id):
        if not api_id:
            self.error("Please provide a valid API ID")

        response = self.client.create_deployment(
            restApiId=api_id,
            stageName="fireprox",
            stageDescription="FireProx Prod",
            description="FireProx Production Deployment",
        )
        resource_id = response["id"]
        return (resource_id, f"https://{api_id}.execute-api.{self.region}.amazonaws.com/fireprox/")

    def get_resource(self, api_id):
        if not api_id:
            self.error("Please provide a valid API ID")
        response = self.client.get_resources(restApiId=api_id)
        items = response["items"]
        for item in items:
            item_id = item["id"]
            item_path = item["path"]
            if item_path == "/{proxy+}":
                return item_id
        return None

    def get_integration(self, api_id):
        if not api_id:
            self.error("Please provide a valid API ID")
        resource_id = self.get_resource(api_id)
        response = self.client.get_integration(restApiId=api_id, resourceId=resource_id, httpMethod="ANY")
        return response["uri"]


def get_region_by_mode(regions: List, mode: str = "all") -> Union[str, List, None]:
    if mode == "all":
        return regions
    elif mode == "random":
        return random.choice(regions)


def parse_region(region: str | List, mode: str = "all") -> Union[str, List, None]:
    """Parse 'region' and return the final region or set of regions according
    to mode
    """
    if region is None:
        return None
    if mode not in ["all", "random"]:
        raise ValueError("mode should one of ['all', 'random']")

    if isinstance(region, str):
        # if region is a file containing regions, read from it
        if os.path.isfile(region):
            with open(region) as f:
                regions = [reg.strip() for reg in f.readlines()]
                return get_region_by_mode(regions, mode)
        elif "," in region:
            regions = region.split(sep=",")
            return get_region_by_mode(regions, mode)
        else:
            return region

    elif isinstance(region, list):
        return get_region_by_mode(region, mode)
