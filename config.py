#!/usr/bin/env python

import argparse
import os
import yaml

dir_path = os.path.dirname(os.path.realpath(__file__))
spack_version='v0.14.1'

parser=argparse.ArgumentParser(description='Small config script which can be used to install a spack instance with the correct configuration files and mch spack packages.')
parser.add_argument('-i', '--idir', type=str, default=dir_path, help='Where the Spack instance is installed or you want it to be installed')
parser.add_argument('-m', '--machine', type=str, help='Required: machine name')
parser.add_argument('-v', '--version', type=str, default='v0.14.1', help='Spack version, Default: ' + spack_version)
parser.add_argument('-r', '--reposdir', type=str, help='repos.yaml install directory')
parser.add_argument('-p', '--pckgidir', type=str, help='Define spack package, modules & stages installation directory. Default: tsa; /scratch/$USER/spack, daint; /scratch/snx3000/$USER/spack')
args=parser.parse_args()

if args.machine is None:
    print('Error: machine name required!')
    exit()
  
if args.idir is not None:
    if not os.path.isdir(args.idir + '/spack'):
        print('Cloning spack instance to: ' + args.idir)
        if args.version is None:
            args.version = spack_version
        clone_cmd = 'git clone git@github.com:spack/spack.git -b' + args.version + ' ' + args.idir + '/spack'   
        os.system(clone_cmd)
print('Installing mch packages & ' + args.machine + ' config files')

if args.reposdir is not None:
    if os.path.isdir(args.reposdir) and not os.path.isfile(args.reposdir + '/repos.yaml'):
        repos_data = yaml.safe_load(open('./sysconfigs/repos.yaml', 'r+'))
        repos_data['repos'] = [dir_path]
        yaml.safe_dump(repos_data, open('./sysconfigs/repos.yaml', 'r+'), default_flow_style=False)
        print('Installing repos.yaml on ' + args.reposdir)
        os.popen('cp ' + dir_path + '/sysconfigs/repos.yaml ' + args.reposdir)

# configure config.yaml

config_data = yaml.safe_load(open('sysconfigs/config.yaml', 'r+'))

if args.pckgidir is None:
    if 'admin' in args.machine:
        args.pckgidir = '/project/g110'
    elif args.machine == 'tsa':
        args.pckgidir = '/scratch/$user/spack'
    elif args.machine == 'daint':
        args.pckgidir = '/scratch/snx3000/$user/spack'
      
config_data['config']['install_tree'] = args.pckgidir + '/spack-install/' + args.machine.replace('admin-', '')
config_data['config']['build_stage'] = [args.pckgidir + '/spack-stages/' + args.machine.replace('admin-', '')]
config_data['config']['module_roots']['tcl'] = args.pckgidir + '/modules'
yaml.safe_dump(config_data, open('./sysconfigs/config.yaml', 'r+'), default_flow_style=False)

# copy modified config.yaml file in site scope of spack instance
os.popen('cp -rf sysconfigs/config.yaml ' + args.idir + '/spack/etc/spack')

# copy modified upstreams.yaml if not admin
if not 'admin' in args.machine:
    upstreams_data = yaml.safe_load(open('./sysconfigs/upstreams.yaml', 'r+'))
    upstreams_data['upstreams']['spack-instance-1']['install_tree'] = '/project/g110/spack-install/' + args.machine.replace('admin-', '')
    yaml.safe_dump(upstreams_data, open('./sysconfigs/upstreams.yaml', 'r+'), default_flow_style=False)
    os.popen('cp -rf sysconfigs/upstreams.yaml ' + args.idir + '/spack/etc/spack')

# copy modules.yaml, packages.yaml and compiles.yaml files in site scope of spack instance
os.popen('cp -rf sysconfigs/' + args.machine.replace('admin-', '') + '/* ' +  args.idir + '/spack/etc/spack')

print('MCH Spack installed.')