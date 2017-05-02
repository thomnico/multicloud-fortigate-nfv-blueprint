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
from cloudify.exceptions import NonRecoverableError

from neutron_plugin.network import NETWORK_OPENSTACK_TYPE


@operation
@with_neutron_client
def add_interface_router(neutron_client, args, **kwargs):
    router_id = args.get('router_id')
    # subnet_id = args.get('subnet_id')
    port_id = args.get('port_id')
    neutron_client.add_interface_router(router_id, {'port_id': port_id})
