# #######
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
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
'''
    Fortinet.FortiGate.Generic
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    Low-level functions
'''

from cloudify import ctx
from cloudify.decorators import operation
from cloudify.exceptions import NonRecoverableError, RecoverableError
import fabric.api
import fabric.state
from fabric.exceptions import NetworkError, CommandTimeout

# pylint: disable=R0903


class Generic(object):
    '''
        Generic, low-level interface for interacting with a FortiGate
        device via SSH

    :param dict ssh_config:
        Key-value pair that get sent to `fabric.api.settings`
    '''
    def __init__(self, ssh_config):
        # Set the SSH configuration options
        self.ssh_config = ssh_config
        if not isinstance(self.ssh_config, dict):
            raise NonRecoverableError(
                'ssh_config is required to be of type dict')
        # Set SSH defaults
        if self.ssh_config.get('use_shell') is None:
            self.ssh_config['use_shell'] = False
        if self.ssh_config.get('always_use_pty') is None:
            self.ssh_config['always_use_pty'] = False
        if self.ssh_config.get('command_timeout') is None:
            self.ssh_config['command_timeout'] = 10

    def execute(self, command):
        '''
            Low-level method for executing SSH commands

        :param string command:
            SSH command to execute (passed directly to `fabric.api.run`)
        :rtype: fabric.operations._AttributeString
        returns: SSH stdout
        :raises: :exc:`cloudify.exceptions.RecoverableError`,
                 :exc:`cloudify.exceptions.NonRecoverableError`
        '''
        # Set Fabric DEBUG output
        fabric.state.output.debug = True
        # Execute the command
        ctx.logger.info('Executing {0}'.format(command))
        try:
            with fabric.api.settings(**self.ssh_config):
                return fabric.api.run(command)
        except NetworkError as ex:
            raise RecoverableError(ex)
        except CommandTimeout as ex:
            raise RecoverableError(ex)

@operation
def command_verify(command, verify, ssh_config, retry=False, **_):
    '''Generic config create operation'''
    # Create the configuration
    iface = Generic(ssh_config)
    result = iface.execute(command)
    for thing_to_verify in verify:
        if thing_to_verify not in result:
            ctx.operation.retry(
                '{0} not in {1}'.format(thing_to_verify, command)
            )
    # Set runtime properties
    ctx.instance.runtime_properties['ssh_config'] = ssh_config
    ctx.instance.runtime_properties['command'] = command

@operation
def execute_commands(commands, ssh_config, **_):
    '''Generic config create operation'''
    # Create the configuration
    iface = Generic(ssh_config)
    result = iface.execute('\n'.join(commands))
    # Set runtime properties
    ctx.instance.runtime_properties['ssh_config'] = ssh_config
    ctx.instance.runtime_properties['command'] = commands

@operation
def execute_commands_filter_for_result(commands, filter_command, matcher, ssh_config, **_):
    '''Generic config create operation'''
    # Create the configuration

    iface = Generic(ssh_config)

    for command in commands:
        commands_result = iface.execute(command)
        ctx.logger.debug('{0} result: {1}'.format(command, commands_result))

    result_command_result = iface.execute(filter_command)

    for result in result_command_result.split('\n'):
        if all(match.lower() in result.lower() for match in matcher):
            success = True

    if not success:
        ctx.operation.retry(
            '{0} not in {1}'.format(matcher, result_command_result)
        )

    ctx.instance.runtime_properties['ssh_config'] = ssh_config
    ctx.instance.runtime_properties['command'] = commands

