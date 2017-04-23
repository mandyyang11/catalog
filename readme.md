# Description
- Developed a content management system using the Flask framework in Python
- Enabled authentication via OAuth with Google account and all data is stored within a PostgreSQL database 
- Featured 2 initial users, 9 categories of sporting goods, and 9 items; new users are able to create new logins and add/delete items for themselves

![website screenshot](image/Screenshot.png?raw=true)

# Steps to run the code:
1. Install VirtualBox from https://www.virtualbox.org/
2. Install Vagrent from https://www.vagrantup.com/
3. Clone fullstack-nanodegree-vm repository via "git clone https://github.com/udacity/fullstack-nanodegree-vm"
4. Change directory to vagrant via "cd fullstack-nanodegree-vm/vagrant"
5. Run the virtual machine via "vagrant up"
6. ssh to virtual machine via "vagrant ssh"
7. Copy or replace the upzipped project file with the catalog folder in fullstack-nanodegree-vm/vagrant
8. Change directory to the project file via "cd /vagrant/catalog"
9. Start the code via "python project.py"
10. Go to "localhost:8000" in the browser of your choice and enjoy the catalog app :)