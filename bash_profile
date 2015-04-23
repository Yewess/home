# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
	. ~/.bashrc
fi

# User specific environment and startup programs

PATH=$PATH:$HOME/bin

export PATH
export EDITOR=/usr/bin/vim
export VIEWER=/usr/bin/vim

# Send sound through ssh
if [ -n "$SSH_CLIENT" ] && [ -x "/usr/bin/pax11publish" ]
then
    eval $(pax11publish -i)
fi

if [ -z "$SSH_AGENT_PID" ]
then
    eval $(ssh-agent -s -t 8H)
fi

export SSH_AGENT_PID
export SSH_AUTH_SOCK
