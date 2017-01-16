# Install Archlinux Tharyrok
## No chroot
### Init
Create partitions before continuing, you may need to restart

### Get latest boostrap
```
wget -O/tmp/archlinux-bootstrap.tar.gz https://archlinux.cu.be/iso/latest/$(wget -q -O- https://archlinux.cu.be/iso/latest/ | grep -E "archlinux-bootstrap-.*-x86_64.tar.gz</a>" | cut -d'"' -f2)
cd /tmp
tar xzf /tmp/archlinux-bootstrap.tar.gz

/tmp/root.x86_64/bin/arch-chroot /tmp/root.x86_64/
```
### Init chroot
```
pacman-key --init
pacman-key --populate archlinux

mv /etc/pacman.d/mirrorlist /etc/pacman.d/mirrorlist.backup
sed -i 's/^#Server/Server/' /etc/pacman.d/mirrorlist.backup
rankmirrors -n 6 /etc/pacman.d/mirrorlist.backup > /etc/pacman.d/mirrorlist

pacman -Suy
```

### Partition First
```
pacman -Sy xfsprogs lvm2 cryptsetup


pvcreate /dev/sdaX
vgcreate root /dev/sdaX

lvcreate -L 30G -n lvroot root
lvcreate -L XXXM -n swap root
lvcreate -L 1024M -n tmp root
lvcreate -l 95%FREE -n home root


cryptsetup luksFormat -c aes-xts-plain64 -s 512 /dev/mapper/root-lvroot
cryptsetup open /dev/mapper/root-lvroot root

mkfs.xfs /dev/mapper/root

mount /dev/mapper/root /mnt
mkdir /mnt/{boot,home}

mount /dev/sdaX /mnt/boot
```

### Base and base-devel
```
pacstrap /mnt base base-devel xfsprogs lvm2 cryptsetup
```

## chroot
```
genfstab -U -p /mnt >> /mnt/etc/fstab
arch-chroot /mnt
```

### Partition Second
```
mkdir -m 700 /etc/luks-keys
dd if=/dev/random of=/etc/luks-keys/home bs=1 count=256 status=progress

cryptsetup luksFormat -v -s 512 /dev/mapper/root-home /etc/luks-keys/home
cryptsetup -d /etc/luks-keys/home open /dev/mapper/root-home home

mkfs.xfs /dev/mapper/home
mount /dev/mapper/home /home
```

Add `/etc/crypttab`
```
swap	/dev/mapper/root-swap		/dev/urandom		swap,cipher=aes-xts-plain64,size=256
tmp		/tmp/dev/mapper/root-tmp	/dev/urandom		tmp,cipher=aes-xts-plain64,size=256
home	/dev/mapper/root-home		/etc/luks-keys/home
```

### Créate environement

Edit sudo

Add user : 
```
useradd -g users -G sys,disk,wheel,uucp,video,audio,optical,storage,input,power -m Tharyrok
passwd tharyrok
su -l tharyrok
```

### Install pacaur and all package

```
curl -s https://gist.githubusercontent.com/Tadly/0e65d30f279a34c33e9b/raw/pacaur_install.sh | bash

pacaur -S - < $(curl -s https://raw.githubusercontent.com/Tharyrok/dotfile/master/package_list.txt)
```

### Enable services

```
systemctl enable pcscd.socket
systemctl enable lightdm.service
```

### Config OS
```
nano /etc/hostname
nano /etc/hosts

ln -s /usr/share/zoneinfo/Europe/Brussels /etc/localtime

nano  /etc/locale.gen
locale-gen

echo KEYMAP=fr > /etc/vconsole.conf
echo KEYMAP=be-latin1 > /etc/vconsole.conf

nano /etc/mkinitcpio.conf
HOOKS="base udev autodetect modconf keymap keyboard block lvm2 encrypt filesystems fsck"

pacman -Rsn linux

mkinitcpio -p linux-lts

nano /etc/default/grub
GRUB_CMDLINE_LINUX_DEFAULT="cryptdevice=/dev/mapper/sys-lvroot:root"
grub-mkconfig -o /boot/grub/grub.cf

nano /etc/fstab
# /dev/mapper/home
/dev/mapper/home        /home           xfs             rw,relatime,attr2,inode64,noquota       0 2

/dev/mapper/tmp         /tmp    tmpfs           defaults        0       0
/dev/mapper/swap        none    swap            sw              0       0

nano /etc/X11/xorg.conf.d/10-keyboard-layout.conf
Section "InputClass"
    Identifier         "Keyboard Layout"
    MatchIsKeyboard    "yes"
    Option             "XkbLayout"  "be"
    Option             "XkbLayout"  "fr"
    Option             "XkbVariant" "latin9" # accès aux caractères spéciaux plus logique avec "Alt Gr" (ex : « » avec "Alt Gr" w x)
EndSection
```


```
wget https://github.com/Tharyrok/dotfile/archive/master.zip -O/tmp/master.zip


```
https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-75308.jpg
https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-154037.jpg
https://wallpapers.wallhaven.cc/wallpapers/full/wallhaven-72207.jpg
