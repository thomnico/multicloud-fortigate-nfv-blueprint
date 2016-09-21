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

from cloudify import ctx
from cloudify.decorators import operation
from openstack_plugin_common import (
    with_neutron_client,
    OPENSTACK_ID_PROPERTY,
    OPENSTACK_NAME_PROPERTY
)

from neutron_plugin.network import NETWORK_OPENSTACK_TYPE


@operation
@with_neutron_client
def update(neutron_client, args, **kwargs):

    subnets = neutron_client.list_subnets(
        name=ctx.target.instance.runtime_properties[OPENSTACK_NAME_PROPERTY]
    )

    subnet = subnets['subnets'][0]
    subnet_id = ctx.target.instance.runtime_properties[OPENSTACK_ID_PROPERTY]
    subnet_body = {}
    subnet_body.update(**args)
    body = {'subnet': subnet_body}

    ctx.logger.debug(
        'Data being sent to neutron_client.update_subnet: subnet: {0}, body: {1}'
        .format(subnet, body)
    )

    s = neutron_client.update_subnet(subnet_id, body)

    ctx.logger.debug('Returned by update: {0}'.format(s))
