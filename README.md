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
```