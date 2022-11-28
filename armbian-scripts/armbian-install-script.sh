### Installing googleNoteToThermal dependencies on NanoPiNeo Running Armbian
### Version: Armbian 22.08 Bullseye Kernel 5.15.y Release date: Oct 22, 2022 Downloaded/Installed/Upgraded/Updated: 11.27.22

sudo apt-get update -y
sudo apt-get upgrade -y
sudo apt-get install python3-pip -y
sudo apt-get install libjpeg-dev -y
sudo apt-get install zlib1g-dev
sudo apt-get install python3-dev -y

# I find that Pillow has choked when building on Armbian in the past...
# So if you have problems, you can use `sudo MAX_CONCURRENCY=1 sudo pip3 install Pillow`

pip3 install Pillow

# escpos will install Pillow as well but again, I installed before for reasons mentioned.

pip3 install escpos
pip3 install gkeepapi
sudo apt-get install scons

# pip3 install keyring # Still haven't gotten keyring to compile on Arbmian due to compiler error.
# Key ring module has been removed from Armbian script for now.

### Installing Epson drivers on Debian
# https://github.com/groolot/epson-tm-t88v-driver/blob/master/INSTALL.md

sudo apt-get install build-essential autoconf autoconf-archive automake libcups2-dev libcupsimage2-dev cups -y

git clone https://github.com/groolot/epson-tm-t88v-driver
cd epson-tm-t88v-driver
autoreconf -fiv
./configure --prefix=/usr
make && make install

# ***Connect the Epson printer to USB port of NanoPi Neo***

sudo cupsctl --remote-any
sudo /etc/init.d/cups restart

# Connect the Epson printer 
# Go to the following address to access CUPS
# https://NANOPINEOSIPADDRESSHERE:631/admin/

# When I accessed CUPs interface Epson appeared as 'Unknown' device as radial button.
# Go through the prompts, selecting all the default values

### Select the option to Choose a PPD File. Select the one in this repo, located here:
# https://github.com/ijjy303/googleNotesToThermal/blob/main/armbian-scripts/epson-tm-t88v-rastertotmt88v.ppd

# When I printed a test page, Epson did feed paper however CUPs logged an error
# This was inconsequential as the escpos library was able to interface with it as expected.

### Extra unrelated but useful dependencies usually requiring install when a python library fails to compile/install on a SBC/Armbian/Raspi device

#sudo apt-get install python3 python-dev python3-dev \
#     build-essential libssl-dev libffi-dev \
#     libxml2-dev libxslt1-dev zlib1g-dev \
#     python-pip
