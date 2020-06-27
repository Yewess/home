# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

export EDITOR=/usr/bin/vim
export VIEWER=/usr/bin/vim
export SYSTEMD_LESS=FRXMK
export SYSTEMD_PAGER=less
export GOPATH="$HOME/go"
export PATH=$HOME/bin:$GOPATH/bin:$PATH
