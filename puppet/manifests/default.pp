# Deploy commander puppet 

Exec { path => [ '/bin/', '/sbin/', '/usr/bin/', '/usr/sbin/', '/usr/local/bin'] }

exec { "apt-update":
    command => "apt-get update"
}

exec { "python-pip":
	command => "apt-get -y install python-pip",
	require => Exec['apt-update']
}

exec { "python-dev":
	command => "apt-get -y install python-dev",
	require => Exec['apt-update']
}

exec { "pip-virtualenv":
	command => "pip install virtualenv",
	require => Exec["python-pip", "python-dev"]
}

exec { "project-virtualenv":
	command => "virtualenv /home/vagrant/environment",
	require => Exec["pip-virtualenv", "python-dev"],
	creates => '/home/vagrant/environment',
	user => "vagrant",
	group => "vagrant"
}

exec { "install-git":
	command => "apt-get -y install git",
	require => Exec['apt-update']
}

exec { "checkout-example":
	command => "git clone https://github.com/munstermedia/deploy-commander-example.git /home/vagrant/deploy-commander-example",
	require => Exec['install-git'],
	creates => '/home/vagrant/deploy-commander-example',
	user => "vagrant",
	group => "vagrant"
}

exec { "install-deploy-commander":
	command => "/home/vagrant/environment/bin/pip install deploy-commander --upgrade",
	require => Exec["project-virtualenv", "python-dev"],
	user => "vagrant",
	group => "vagrant"
}
