# .bashrc

# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi

alias diff='diff -Naur'
alias sshx='ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o CheckHostIP=no -F /dev/null -i $HOME/.ssh/libra.pem'
alias scpx='scp -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -o CheckHostIP=no -F /dev/null -i $HOME/.ssh/libra.pem'
alias pgcloud='sudo podman run -it --rm -e AS_ID=$UID -e AS_USER=$USER -v /home/$USER:$HOME --security-opt label=disable quay.io/cevich/gcloud_centos:latest'
alias pgsutil='sudo podman run -i --rm -e AS_ID=$UID -e AS_USER=$USER -v /home/$USER:$HOME --security-opt label=disable quay.io/cevich/gsutil_centos:latest'
alias ll='ls -l'
alias la='ls -A'
alias dd='dd status=progress'
alias _='sudo'

# Share packaging cache across fedora distros
# Usae: podman_fedora <release-number> <podman args>
podman_fedora() {
    local release="$1"
    shift
    local host_cachedir="$HOME/.cache/containers/fedora-${release}/var/cache/dnf"
    local cnt_cachedir="/var/cache/dnf"
    mkdir -p "$host_cachedir"
    set -x
    podman "$@" --volume=${host_cachedir}:${cnt_cachedir}:Z registry.fedoraproject.org/fedora:$release
    ret=$?
    set +x
    return $ret
}

podman_run_fedora() {
    local release="$1"
    shift
    podman_fedora $release run "$@"
}

podman_build_fedora() {
    local release="$1"
    shift
    podman_fedora $release build "$@"
}

# don't put duplicate lines or lines starting with space in the history.
# See bash(1) for more options
HISTCONTROL=ignoreboth

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# The next line updates PATH for the Google Cloud SDK.
if [ -f '/home/cevich/google-cloud-sdk/path.bash.inc' ]; then . '/home/cevich/google-cloud-sdk/path.bash.inc'; fi

# The next line enables shell command completion for gcloud.
if [ -f '/home/cevich/google-cloud-sdk/completion.bash.inc' ]; then . '/home/cevich/google-cloud-sdk/completion.bash.inc'; fi
