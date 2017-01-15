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

## Partition First
```
pvcreate /dev/sdaX
vgcreate root /dev/sdaX

lvcreate -L 30G -n lvroot root
lvcreate -L XXXM -n swap root
lvcreate -L 1024M -n tmp root
lvcreate -l 95%FREE -n home root


cryptsetup luksFormat -c aes-xts-plain64 -s 512 /dev/mapper/root-lvroot
cryptsetup open /dev/mapper/root-lvroot root

pacman -Sy xfsprogs
mkfs.xfs /dev/mapper/root

mount /dev/mapper/root /mnt
mkdir /mnt/{boot,home}

mount /dev/sdaX /mnt/boot

```