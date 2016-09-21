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
    Fortinet.FortiGate.Config
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Low-level configuration subsystem interface
'''

from cloudify import ctx
from cloudify.decorators import operation
from fortigate.generic import Generic

# pylint: disable=R0201


class Config(Generic):
    '''
        FortiGate interface for performing CRUD operations on
        the configuration subsystem

    :param dict ssh_config:
        Key-value pair that get sent to `fabric.api.settings`
    '''

    def __init__(self, ssh_config, name=None, cid=None):
        # Init the inherited class
        Generic.__init__(self, ssh_config)
        self.name = name
        self.cid = cid

    def create(self, params, name=None, cid=None):
        '''
            Creates a FortiGate config entry

        :param dict params:
            Key-value pairs of configuration parameters to set
        :param string name:
            Name of the configuration element (eg. "firewall policy")
        :param string cid:
            Name of the specific configuration ID to edit
        '''

        def handle_config(name, cid, config_tree, commands_list):
            # Run SET commands
            commands.append('config {0}'.format(name))
            commands.append('edit {0}'.format(cid))
            for config in config_tree:
                for key, val in config.iteritems():
                    if key == 'nested_config':
                        commands_list = handle_config(val['config_name'],
                                                      val['config_id'],
                                                      val['config'],
                                                      commands_list)
                    else:
                        if isinstance(val, list):
                            val = '{0}'.format(' '.join(str(v) for v in val))
                        else:
                            val = '{0}'.format(val)
                        commands_list.append('set {0} {1}'.format(key, val))
            # End "config" mode
            commands_list.append('end')
            return commands_list

        name = name or self.name
        cid = cid or self.cid
        ctx.logger.debug('Running config updates on "%s (%s)"', name, cid)
        # Skip if there's no key-value pairs
        if not params:
            ctx.logger.warn(
                'No key-value pairs provided for config.')
            # return
        commands = []
        # Start in "config" mode
        # Switch to "edit" mode
        commands = handle_config(name, cid, params, commands)

        # Run the command
        output = self.execute('\n'.join(commands))
        ctx.logger.debug('[REMOTE] {0}'.format(output))

    def read(self, name=None, cid=None):
        '''
            Reads in a FortiGate config entry

        :param string name:
            Name of the configuration element (eg. "firewall policy")
        :param string cid:
            Name of the specific configuration ID to delete
        '''
        name = name or self.name
        cid = cid or self.cid
        ctx.logger.debug('Running show config on "%s (%s)"', name, cid)
        # Run the command
        return self.parse_output(
            self.execute('show {0} {1}'.format(name, cid)))

    def update(self, params, name=None, cid=None):
        '''
            Updates a FortiGate config entry

        :param string name:
            Name of the configuration element (eg. "firewall policy")
        :param string cid:
            Name of the specific configuration ID to edit
        :param dict params:
            Key-value pair of configuration parameters to set
        '''
        name = name or self.name
        cid = cid or self.cid
        self.create(name, cid, params)

    def delete(self, name=None, cid=None):
        '''
            Deletes a FortiGate config entry

        :param string name:
            Name of the configuration element (eg. "firewall policy")
        :param string cid:
            Name of the specific configuration ID to delete
        '''
        name = name or self.name
        cid = cid or self.cid
        ctx.logger.debug('Running config delete on "%s (%s)"', name, cid)
        output = self.execute('\n'.join([
            # Start in "config" mode
            'config {0}'.format(name),
            # Delete the entry
            'delete {0}'.format(cid),
            # End "config" mode
            'end']))
        ctx.logger.debug('[REMOTE] {0}'.format(output))

    def parse_output(self, raw_output):
        '''Converts raw output to a dict of config data'''
        props = dict()
        if not isinstance(raw_output, basestring):
            return None
        # Split by newline and strip whitespace
        output = [x.strip() for x in raw_output.rsplit('\n')]
        # Locate "set" lines, split by whitespace twice max, grab the
        # last two strings (key and val, excluding the word "set")
        opts = [x.rsplit(' ', 2)[1:] for x in output if x.startswith('set ')]
        # Strip out the quotation marks (which are seemingly arbitrarily placed)
        for opt in opts:
            props[opt[0]] = opt[1].strip('"')
        return props


@operation
def create(config_name, config_id, config, ssh_config, **_):
    '''Generic config create operation'''
    # Create the configuration
    iface = Config(name=config_name,
                   cid=config_id,
                   ssh_config=ssh_config)
    iface.create(config)
    # Set runtime properties
    ctx.instance.runtime_properties['ssh_config'] = ssh_config
    ctx.instance.runtime_properties['config_name'] = config_name
    ctx.instance.runtime_properties['config_id'] = config_id
    ctx.instance.runtime_properties['config'] = iface.read()
    # Dump the runtime properties
    ctx.logger.debug('Runtime properties: {0}'.format(
        ctx.instance.runtime_properties))


@operation
def delete(**_):
    '''Generic config delete operation'''
    # Delete the config item
    Config(
        name=ctx.instance.runtime_properties.get('config_name'),
        cid=ctx.instance.runtime_properties.get('config_id'),
        ssh_config=ctx.instance.runtime_properties.get('ssh_config')
    ).delete()
