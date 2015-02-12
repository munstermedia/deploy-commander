# == Class: uwsgi
#
# Installs uwsgi
#
class uwsgi {
  package {'uwsgi':
    ensure => present,
    provider => pip
  }

  file { '/etc/init/uwsgi.conf':
    source  => 'puppet:///modules/uwsgi/uwsgi.conf',
    require => Package['uwsgi'];
  }
  
  file { "/etc/uwsgi":
      ensure => "directory",
      owner => 'www-data',
      group => 'www-data',
      mode => 775;
  }
  
  file { "/etc/uwsgi/vassals/":
      ensure => "directory",
      owner => 'www-data',
      group => 'www-data',
      mode => 775;
  }
}
