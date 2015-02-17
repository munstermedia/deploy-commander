# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "deploycommander" do |deploycommander|
	  # Use ubuntu trusty box
	  deploycommander.vm.box = "ubuntu/trusty64"
	  
	  # Define fetch box
	  deploycommander.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
	
	  # Foreward port 80 to devserver port
	  # deploycommander.vm.network :forwarded_port, guest: 80, host: 8000
	
	  deploycommander.vm.network :private_network, ip: "192.168.56.166"
	  deploycommander.vm.synced_folder "./", "/deploy_commander/", :owner => "www-data", :group => "www-data"
  
  	config.vm.provision :puppet do |puppet|
    	puppet.manifests_path = 'puppet/manifests'
    	puppet.manifest_file = 'default.pp'
    	puppet.module_path = 'puppet/modules'
  	end
  
  end
  
  
  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    #vb.gui = true
  
    vb.customize ["modifyvm", :id, "--cpus", "1"]
	vb.customize ["modifyvm", :id, "--memory", "512"]
  end
end