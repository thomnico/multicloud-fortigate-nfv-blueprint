# Multicloud NVF Example

## Requirements

* Openstack Kilo Tenant + Account Credentials
* AWS Account and privileges to create: VPC, SUBNET, Internet Gateway, Route Tables, VPN Gateway, Customer Gateway, NAT Instances, Servers, Security Groups, Elastic IPs, Keys, DHCP Options Set, VPC Connection,
* Licensed Fortigate VM Snapshot in your Openstack Project

## Contents

In short this blueprint creates an AWS Environment and an Openstack Environment. The two are connected with an IPSec consisting of a Fortigate VM in Openstack connected with AWS VPC Connection. A Cloudify Manager is located in AWS and manages both environments.

* Openstack Environment
  * 2 Networks, each with a single subnet
  * 1 Router
  * Security Group
  * Key
  * Fortigate IPSec Server

* AWS Environment (Follows Scenario 2 Network Architecture)
  * VPC
  * 2 Subnets
  * Internet Gateway
  * NAT Instance
  * Security Groups
  * Elastic IPs
  * Keypairs
  * Customer Gateway
  * VPN Gateway
  * VPN Connection (Configuration with Fortigate in Openstack included.)
  * Cloudify Manager

## Instructions:

* Create your inputs file. An example is provided.
* Run this command: `cfy install -p multicloud-nfv-blueprint/blueprint.yaml --task-retry-interval=10 --task-retries=25 -i inputs.yaml`

