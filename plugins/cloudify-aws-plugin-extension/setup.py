#########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.

from setuptools import setup


setup(
    name='cloudify-aws-plugin-extension',
    version='0.1.0.dev0',
    author='earthmant',
    author_email='trammell@gigaspaces.com',
    packages=[
        'cloudify_aws_vpc_extension'
    ],
    license='LICENSE',
    description='Extension to Cloudify plugin for AWS infrastructure.',
    dependency_links=[
        'https://github.com/cloudify-cosmo/cloudify-aws-plugin/tarball/1.4.2#egg=cloudify-aws-plugin-1.4.2'
    ],
    install_requires=[
        'cloudify-aws-plugin>=1.4.2',
        'xmltodict'
    ]
)
