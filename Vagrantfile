# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.define "web1" do |web1|
	  # Use ubuntu trusty box
	  web1.vm.box = "ubuntu/trusty64"
	  
	  # Define fetch box
	  web1.vm.box_url = "http://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
	
	  # Foreward port 80 to devserver port
	  # web1.vm.network :forwarded_port, guest: 80, host: 8000
	
	  web1.vm.network :private_network, ip: "192.168.56.111"
	  web1.vm.synced_folder "./../", "/project/", :owner => "www-data", :group => "www-data"
  end
  
  
  config.vm.provider :virtualbox do |vb|
    # Don't boot with headless mode
    #vb.gui = true
  
    #vb.customize ["modifyvm", :id, "--cpus", "1"]
    vb.customize ["modifyvm", :id, "--memory", "1024"]
  end
end
