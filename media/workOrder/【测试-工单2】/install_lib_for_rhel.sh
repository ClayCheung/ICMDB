#!/bin/bash
#0 : not exist; 1 : exist
YUM_REPO_IS_EXIST=0

YUM_REPOS_PATH="/etc/yum.repos.d/"
TAR_FILE="rhel-source.tar.gz"
TMP_REPOS=${YUM_REPOS_PATH}"rhel-source0.repo"
RPM_KEY_FILE="/etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release"
ONLY_PREPARE=0

function output_red_msg()
{
    local msg="$1"
    echo -e "\033[0m\\033[1;31m"   "${msg} \033[0m"
}

function pre_install_check()
{
    local os_ver="`cat /etc/*-release | grep -E 'release|Server' | head -n 1`"
    echo -e "Prepare : \033[1m check OS [ ${os_ver} ] \033[0m...\c"
    local release_file="/etc/redhat-release"
        local isRedhat="`cat /proc/version | grep -i "Red" |grep -i "Hat"`" > /dev/null 2>&1
    if [ -f "${release_file}" -a -n "${isRedhat}" ] ; then
        echo -e "\033[32m done \033[0m"
    else
        output_red_msg "failed."
        output_red_msg "The install_lib script is not for rhel."
        exit 1
    fi
}

g_drive_name=""
function get_drive_name()
{
    local info_file="/proc/sys/dev/cdrom/info"
    if [ -f "${info_file}" ] ; then
        #drive name
        local tmp_drive_name="$(cat ${info_file} | grep "drive name" | cut -d ":" -f2)"
        #delete the space 
        local first_drive_dev="$(echo ${tmp_drive_name} | cut -d " " -f1)"
        g_drive_name="$(echo ${first_drive_dev})"
    fi
    if [ -n "${g_drive_name}" ]; then
        return 0
    fi
    output_red_msg "Failed to get cd drive name from ${info_file}, try /dev/cdrom"
    g_drive_name="$(ls -r /dev/cdrom*  | head -n 1 | cut -d'/' -f3)"
    if [ -n "${g_drive_name}" ]; then
        return 0
    fi
    output_red_msg "Failed to get cd drive name from /dev/cdrom, try /dev/sr"
    g_drive_name="$(ls -r /dev/sr*  | head -n 1 | cut -d'/' -f3)"
    if [ -n "${g_drive_name}" ]; then
        return 0
    fi
    output_red_msg "Failed to get cd drive name from /dev/sr"
    output_red_msg "Please check your cd driver"
    exit 1
}

function set_local_pkg_source()
{
    echo -e "Prepare : \033[1m mount OS and configure yum source \033[0m...\c"
    
    if [ $# -eq 0 ]; then
        get_drive_name
        #easy to find the reason that cause the mount failed
        mount /dev/${g_drive_name} /mnt || {
            output_red_msg " mount failed."
            exit 1
        }
    elif [ $# -eq 1 ]; then
        local iso_file=$1;
        if [ ! -f ${iso_file} ]; then
            output_red_msg "iso file not exit"	
            exit 1
        fi
        mount -o loop $iso_file /mnt || {
            output_red_msg " mount failed."
            exit 1
        }
    else
        output_red_msg "input para error"
        exit 1
    fi
    
    rpm --import ${RPM_KEY_FILE}  > /dev/null 2>&1
    #backup yum source
    cd ${YUM_REPOS_PATH}  > /dev/null 2>&1
    if [ 0 -ne $? ]; then
        output_red_msg "${YUM_REPOS_PATH} path is not exit"	
        exit 1
    fi
    tar zvcf ${TAR_FILE} * --remove-files  > /dev/null 2>&1
    cd -  > /dev/null 2>&1

#configure new yum source
cat <<eof > ${TMP_REPOS}
[rhel-source]
name=Red Hat Enterprise Linux $releasever - $basearch - Source
baseurl=file:///mnt
enabled=1
gpgcheck=0
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-redhat-release
skip_if_unavailable = True
eof

    yum clean all  > /dev/null 2>&1
    yum list  > /dev/null 2>&1
    echo -e "\033[32m done \033[0m"
    if [ "1" -eq "${ONLY_PREPARE}" ] ; then        
        exit 0
    fi
    return 0
}

g_base_pkg_group_number=3
g_base_pkg_group_0=(additional-devel base compat-libraries core development)
g_base_pkg_group_1=(fonts graphical-admin-tools hardware-monitoring input-methods internet-browser large-systems)
g_base_pkg_group_2=(network-file-system-client performance perl-runtime system-admin-tools x11)

g_base_pkg_number=5
g_base_pkg_0=(libXinerama-devel xorg-x11-proto-devel startup-notification-devel libXau-devel libgcrypt-devel expect sg3_utils )
g_base_pkg_1=(popt-devel libXrandr-devel libxslt-devel gnutls-devel mtools pax python-dmidecode sgpio genisoimage wodim)
g_base_pkg_2=(jpackage-utils perl-DBD-SQLite ibutils texlive dos2unix ntp crash lftp gcc gcc-c++ gcc-gfortran nfs-utils)
g_base_pkg_3=(libXau.i686 libXau-devel.i686 libxcb.i686 libxcb-devel.i686 libX11.i686 libX11-devel.i686 libstdc++.i686 libstdc++-devel.i686)
g_base_pkg_4=(libXext.i686 libXext-devel.i686 libXi.i686 libXi-devel.i686 libXinerama.i686 libXinerama-devel.i686 libXtst.i686 libXtst-devel.i686 zip unzip)

#handle special packages
#redhat 7.x not to install g_base_pkg_exclude_7
g_base_pkg_exclude_7=(vconfig libgnomeui-devel libbonobo-devel libglade2-devel compat-libstdc++-33.i686)

g_failed_ins_pkg=""
g_failed_ins_pkg_idx=0

function install_pkg()
{
    local pkg_name="$1"
    echo -e "Install : \033[1m ${pkg_name}\033[0m...\c"
    yum -y install "${pkg_name}" > /dev/null 2>&1
    if [ $? -ne 0 ];then
        output_red_msg " failed."
        g_failed_ins_pkg[$g_failed_ins_pkg_idx]="${pkg_name}"
        g_failed_ins_pkg_idx=$(($g_failed_ins_pkg_idx + 1))
        return 1
    fi
    echo -e "\033[32m done \033[0m"
}

function install_xfsprogs_for_rhel()
{
    local xfspgs_pkg="xfsprogs"
    echo -e "Install : \033[1m ${xfspgs_pkg}\033[0m...\c"
    yum -y install "${xfspgs_pkg}" > /dev/null 2>&1
    if [ $? -ne 0 ];then
        if [ -n "`cat /etc/redhat-release|grep "Red Hat"|grep 6.4`" ] && [ "x86_64" == "`uname -m`" ];then
            rpm -ivh --nodeps /mnt/Packages/xfsprogs*.rpm  > /dev/null 2>&1
            local isExist=$(rpm -qa | grep xfsprogs | grep -v ^grep)
            if [ -z "${isExist}" ];then
                output_red_msg " failed."
                g_failed_ins_pkg[$g_failed_ins_pkg_idx]="${xfspgs_pkg}"
                g_failed_ins_pkg_idx=$(($g_failed_ins_pkg_idx + 1))
                return 1
            fi
        elif [ -n "`cat /etc/redhat-release|grep "Red Hat"|grep 6.5`" ] && [ "x86_64" == "`uname -m`" ];then
            rpm -ivh --nodeps /mnt/Packages/xfsprogs*.rpm  > /dev/null 2>&1
            local isExist=$(rpm -qa | grep xfsprogs | grep -v ^grep)
            if [ -z "${isExist}" ];then
                output_red_msg " failed."
                g_failed_ins_pkg[$g_failed_ins_pkg_idx]="${xfspgs_pkg}"
                g_failed_ins_pkg_idx=$(($g_failed_ins_pkg_idx + 1))
                return 1
            fi
        elif [ -n "`cat /etc/redhat-release|grep "Red Hat"|grep "6.6\|6.8"`" ] && [ "x86_64" == "`uname -m`" ];then
            rpm -ivh --nodeps /mnt/ScalableFileSystem/xfsprogs*.rpm  > /dev/null 2>&1
            local isExist=$(rpm -qa | grep xfsprogs | grep -v ^grep)
            if [ -z "${isExist}" ];then
                output_red_msg " failed."
                g_failed_ins_pkg[$g_failed_ins_pkg_idx]="${xfspgs_pkg}"
                g_failed_ins_pkg_idx=$(($g_failed_ins_pkg_idx + 1))
                return 1
            fi
        fi
    fi
    echo -e "\033[32m done \033[0m"
}

function install_non_exclude_pkgs()
{
    if [ -z "`cat /etc/redhat-release|grep "Red Hat"|grep 7.*`" ] ; then
        local arr_size=${#g_base_pkg_exclude_7[@]}
        for((iidx=0;iidx<$arr_size;iidx++))
        {
            local pkg_name="${g_base_pkg_exclude_7[$iidx]}"
            install_pkg $pkg_name
        }
    fi
}

function install_base_pkg_group()
{
    for((idx=0;idx<$g_base_pkg_group_number;idx++))
    {
        local arr_name="g_base_pkg_group_$idx"
        local arr_size=$(eval echo '$'{#$arr_name[@]})
        for((iidx=0;iidx<$arr_size;iidx++))
        {
            local pkg_name="@$(eval echo \${$arr_name[$iidx]})"
            install_pkg $pkg_name
        }
    }
}

function install_base_pkgs()
{
    for((idx=0;idx<$g_base_pkg_number;idx++))
    {
        local arr_name="g_base_pkg_$idx"
        local arr_size=$(eval echo '$'{#$arr_name[@]})
        for((iidx=0;iidx<$arr_size;iidx++))
        {
            local pkg_name="$(eval echo \${$arr_name[$iidx]})"
            install_pkg $pkg_name
        }
    }
}

function uninstall_pkg()
{
    local pkg_name="$1"
    echo -e "Uninstall : \033[1m ${pkg_name}\033[0m...\c"
    yum -y remove "${pkg_name}" > /dev/null 2>&1
    if [ $? -ne 0 ];then
        output_red_msg " failed."
        return 1
    fi
    echo -e "\033[32m done \033[0m"
}

function give_summary_missing_pkgs()
{
    if [ "$g_failed_ins_pkg_idx" -gt "0" ] ; then
        output_red_msg "======  Not be installed packages  ======"
        for((idx=0;idx<$g_failed_ins_pkg_idx;idx++))
        {
            echo "        ${g_failed_ins_pkg[$idx]}"
        }
        
        output_red_msg "1. Make sure that the not installed packages effect none"
        output_red_msg "2. At last, you should reboot the OS [command: shutdown -r now]"
        exit 1
    fi
}

pre_install_check
if [ "0" -eq "${YUM_REPO_IS_EXIST}" ] ; then
    set_local_pkg_source $@
fi

#install packages
install_base_pkg_group
install_base_pkgs
install_non_exclude_pkgs

#special handler
install_xfsprogs_for_rhel
uninstall_pkg NetworkManager

chkconfig firstboot off > /dev/null 2>&1

#recover the default yum source
if [ "0" -eq "${YUM_REPO_IS_EXIST}" ] ; then
    sleep 5
    umount /mnt
    rm -rf ${TMP_REPOS}  > /dev/null 2>&1
    cd ${YUM_REPOS_PATH}  > /dev/null 2>&1
    if [ -f "${TAR_FILE}" ] ; then
        tar zvxf ${TAR_FILE} && rm -rf ${TAR_FILE}  > /dev/null 2>&1
    fi
    cd -  > /dev/null 2>&1
fi

#if failed , exit ; and tell user when failed
give_summary_missing_pkgs

output_red_msg 'reboot the os after 20s'
sleep 20
shutdown -r now
