# == Class: baseconfig
#
# Performs initial configuration tasks for all Vagrant boxes.
#
class baseconfig {
  exec { 'apt-get update':
    command => '/usr/bin/apt-get update';
  }
  
  package { ['python-dev','python-pip', 'nodejs', 'npm']:
    ensure => present;
  }
  
  package {'virtualenv':
    ensure   => installed,
    provider => 'pip'
  }
  
  host { 'hostmachine':
    ip => '192.168.56.166';
  }

  file { '/home/vagrant/.bashrc':
      owner => 'vagrant',
      group => 'vagrant',
      mode  => '0644',
      source => 'puppet:///modules/baseconfig/bashrc';
  }
}
