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

import xmltodict

# Cloudify imports
from cloudify_aws.base import AwsBaseRelationship
from cloudify_aws import connection, constants, utils
from cloudify import ctx
from cloudify.decorators import operation


@operation
def establish(args=None, **_):
    target_aws_config = ctx.target.node.properties['aws_config']
    client = \
        connection.VPCConnectionClient().client(aws_config=target_aws_config)
    return VpnConnectionExtension(client=client).associate(args)

@operation
def propagate_routes(args=None, **_):
    target_aws_config = ctx.target.node.properties['aws_config']
    client = \
        connection.VPCConnectionClient().client(aws_config=target_aws_config)
    return VpnConnectionExtension(client).propagate_routes(args)


class VpnConnectionExtension(AwsBaseRelationship):

    def __init__(self, client=None):
        super(AwsBaseRelationship, self).__init__(
            client=connection.VPCConnectionClient().client()
        )
        self.source_resource_id = \
            ctx.target.instance.runtime_properties.get('vpn_connection', None)
        self.target_resource_id = \
            ctx.target.instance.runtime_properties.get('vpn_connection', None)
        self.source_get_all_handler = {
            'function': self.client.get_all_vpn_connections,
            'argument':
                '{0}_ids'.format('vpn_connection')
        }

    def associate(self, args):
        vpc_connection = self.filter_for_single_resource(
            self.source_get_all_handler['function'],
            {'vpn_connection_ids': self.source_resource_id}
        )
        if 'available' not in vpc_connection.state:
            return ctx.operation.retry(
                'VPN Connection not ready. Usually more than 2 minutes wait. '
            )
        ctx.logger.debug(
            'CONFIGURATION: {0}'.format(vpc_connection.customer_gateway_configuration)
        )
        customer_gateway_configuration = xmltodict.parse(vpc_connection.customer_gateway_configuration)
        ctx.source.instance.runtime_properties['customer_gateway_configuration'] = customer_gateway_configuration
        vpn_config = customer_gateway_configuration.get('vpn_connection')
        vpn_id = vpn_config.get('@id')
        loop_id = 0
        ctx.source.instance.runtime_properties['ipsec_tunnel'] = {}
        for tunnel_config in vpn_config.get('ipsec_tunnel'):
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)] = {}
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['id'] = '{0}-{1}'.format(vpn_id,
                                                                                                          loop_id)
            cgw_config = tunnel_config.get('customer_gateway')
            vgw_config = tunnel_config.get('vpn_gateway')
            ike_config = tunnel_config.get('ike')
            ipsec_config = tunnel_config.get('ipsec')

            key_lifetime = ike_config.get('lifetime')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['keylife'] = key_lifetime

            raw_encryption_protocol = ike_config.get('encryption_protocol').split('-')
            authentication_protocol = ike_config.get('authentication_protocol')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['authentication_protocol'] = \
                authentication_protocol
            proposal = '{0}{1}-{2}'.format(raw_encryption_protocol[0],
                                           raw_encryption_protocol[1],
                                           authentication_protocol)

            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['proposal'] = proposal

            vgw_external_ip = vgw_config.get('tunnel_outside_address').get('ip_address')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['remote-gw'] = vgw_external_ip

            preshared_key = ike_config.get('pre_shared_key')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['psksecret'] = preshared_key

            dh_group = ike_config.get('perfect_forward_secrecy')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['dhgrp'] = dh_group.split('group')[1]

            ipsec_lifetime = ipsec_config.get('lifetime')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['keylifeseconds'] = ipsec_lifetime

            cgw_internal_ip = cgw_config.get('tunnel_inside_address').get('ip_address')
            cgw_netmask = cgw_config.get('tunnel_inside_address').get('network_mask')
            cgw_cidr = cgw_config.get('tunnel_inside_address').get('network_cidr')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['cgw_internal_ip'] = cgw_internal_ip
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['cgw_netmask'] = cgw_netmask
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['cgw_cidr'] = cgw_cidr

            vgw_internal_ip = vgw_config.get('tunnel_inside_address').get('ip_address')
            vgw_netmask = vgw_config.get('tunnel_inside_address').get('network_mask')
            vgw_cidr = vgw_config.get('tunnel_inside_address').get('network_cidr')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['vgw_internal_ip'] = vgw_internal_ip
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['vgw_netmask'] = vgw_netmask
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['vgw_cidr'] = vgw_cidr

            cgw_external_ip = cgw_config.get('tunnel_outside_address').get('ip_address')
            ctx.source.instance.runtime_properties['ipsec_tunnel'][str(loop_id)]['cgw_external_ip'] = cgw_external_ip
            loop_id += 1

        return True

    def propagate_routes(self, args):
        attachment_args = {}
        attachment_args = utils.update_args(attachment_args, args)
        return self.execute(self.client.enable_vgw_route_propagation,
                            attachment_args, raise_on_falsy=True)
