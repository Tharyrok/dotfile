# Install Archlinux Tharyrok
## Get latest boostrap
```
wget https://archlinux.cu.be/iso/latest/archlinux-bootstrap-2017.01.01-x86_64.tar.gz -O/tmp/archlinux-bootstrap.tar.gz
cd /tmp
tar xzf /tmp/archlinux-bootstrap.tar.gz

/tmp/root.x86_64/bin/arch-chroot /tmp/root.x86_64/
```
## Init chroot
```
pacman-key --init
pacman-key --populate archlinux

mv /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
sed -i 's/^#Server/Server/' /etc/pacman.d/mirrorlist.backup
rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist
```
