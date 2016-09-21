########
# Copyright (c) 2015 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

# Cloudify imports
from cloudify_aws.vpc.routetable import RouteTable
from cloudify_aws import constants, utils, connection
from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError


@operation
def set_as_main_route_table(args=None, **_):
    return RouteTableExt().set_as_main_route_table(args)


class RouteTableExt(RouteTable):

    def __init__(self, routes=None):
        super(RouteTable, self).__init__(
            constants.ROUTE_TABLE['AWS_RESOURCE_TYPE'],
            constants.ROUTE_TABLE['REQUIRED_PROPERTIES'],
            client=connection.VPCConnectionClient().client()
        )
        self.not_found_error = constants.ROUTE_TABLE['NOT_FOUND_ERROR']
        self.get_all_handler = {
            'function': self.client.get_all_route_tables,
            'argument':
                '{0}_ids'.format(constants.ROUTE_TABLE['AWS_RESOURCE_TYPE'])
        }

    def set_as_main_route_table(self, args=None):
        vpc = self.get_connected_vpc(ctx.instance.runtime_properties['vpc_id'])
        association_id = None
        for route_table in self.get_vpc_route_tables(vpc.id):
            for association in route_table.associations:
                if association.main:
                    association_id = association.id
                    break
        if not association_id:
            raise NonRecoverableError('No main route table was found')
        create_args = {
            'association_id': association_id,
            'route_table_id': self.resource_id
        }
        create_args = utils.update_args(create_args,
                                        args)
        new_association_id = \
            self.execute(self.client.replace_route_table_association_with_assoc,
                         create_args, raise_on_falsy=True)
        ctx.instance.runtime_properties['association_id'] = new_association_id
        return True

    def get_connected_vpc(self, vpc_id):
        vpc = self.filter_for_single_resource(
            self.client.get_all_vpcs, dict(vpc_ids=vpc_id)
        )
        return vpc

    def get_vpc_route_tables(self, vpc_id):
        route_tables = []
        for matched in self.get_all_matching():
            if vpc_id in matched.vpc_id:
                route_tables.append(matched)
        return route_tables
