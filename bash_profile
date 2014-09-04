# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/bin

export PATH
export EDITOR=/usr/bin/vim
export AUTOTEST_PATH="$HOME/devel/test/autotest"

# Send sound through ssh
if [ -n "$SSH_CLIENT" ] && [ -x "/usr/bin/pax11publish"]
then
    eval $(pax11publish -i)
fi
