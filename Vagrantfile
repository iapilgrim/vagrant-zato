VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.box = "zato-box"
  # config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  # config.vm.box_url = "/Volumes/Data/vagrant/boxes/pgdev.box"  
  config.vm.box_url = "/Volumes/Data/vagrant/precise64.box"    

# Port  Notes
# 11223 Load-balancer's HTTP port (this is what external applications use to invoke services you develop)
# 17010 server1's HTTP port
# 17011 server2's HTTP port
# 8183  Web admin's HTTP port (this is where you point your browser to and log in as an admin user)  
  config.vm.network :forwarded_port, guest: 5432, host: 1234
  config.vm.network :forwarded_port, guest: 11223, host: 5678
  config.vm.network :forwarded_port, guest: 17010, host: 17010
  config.vm.network :forwarded_port, guest: 17011, host: 17011
  config.vm.network :forwarded_port, guest: 8183, host: 8183        


  config.vm.synced_folder Dir.pwd, "/srv/salt"
  config.vm.synced_folder Dir.pwd + "/pillar/", "/srv/pillar"
  config.vm.synced_folder Dir.pwd + "/working/", "/apps/zato/"  

  config.vm.provider "virtualbox" do |v|
    v.name = "zato"
    v.gui = false
  end

  config.vm.hostname = "zato"
  config.ssh.shell = "bash -c 'BASH_ENV=/etc/profile exec bash'"

  config.vm.define "zato" do |z|

    # Repository update & install curl
    z.vm.provision "shell", inline: "apt-get update"
    z.vm.provision "shell", inline: "apt-get -y install curl"

    # Helper programs used for installing
    z.vm.provision "shell", inline: "apt-get -y install apt-transport-https"
    z.vm.provision "shell", inline: "apt-get -y install python-software-properties"

    # Add the package signing key
    z.vm.provision "shell", inline: "curl -s https://zato.io/repo/zato-0CBD7F72.pgp.asc | apt-key add -"

    # Add Zato repo and update sources
    z.vm.provision "shell", inline: "apt-add-repository https://zato.io/repo/stable/ubuntu"
    z.vm.provision "shell", inline: "apt-get update"

    # Install Zato
    z.vm.provision "shell", inline: "apt-get -y install zato"

    # Set the default password
    z.vm.provision "shell", inline: "echo zato:zato | chpasswd"


    z.vm.provision :salt do |salt|
      salt.run_highstate = true
      salt.minion_config = "minion.conf"
      salt.verbose = true
    end  
  end

end
