#!/bin/bash

set -eo pipefail

REPO_ROOT=$(realpath $(dirname "${BASH_SOURCE[0]}")/../)
# Files to simply place into $HOME with a '.' prefix (backing up existing)
DOTFILES="astylerc bash_profile bashrc gitconfig vimrc screenrc tmux.conf"
# Directories to recursively link files into $HOME
DIRS="bin .gnupg .config"

msg() { echo "${1:-No message specified!}" &> /dev/stderr; }

if [[ ! -r "${REPO_ROOT}/README.md" ]] || [[ ! -d "${REPO_ROOT}/.git" ]]; then
    msg "Error: Expecting to find the repository root at '$REPO_ROOT'"
    exit 1
fi

# Always return the full absolute dereferenced path to a possibly missing file
truepath() {
    local filepath="$1"
    if [[ -z "$filepath" ]]; then
        msg "Error: Expecting a non-empty filepath as the first argument"
        exit 7
    fi

    local truefilepath="$filepath"  # Couldn't be resolved for any reason
    # Any bad links/missing files will fallback to the above
    local linkedfile=$(readlink --canonicalize-missing "$filepath" 2>/dev/null)  # empty when not a link
    if [[ -n "$linkedfile" ]]; then
        truefilepath=$(realpath "$linkedfile" 2>/dev/null)  # link may be relative?
    fi
    echo "$truefilepath"
}

install_link(){
    local src=$(truepath "$1")
    local srcname=$(basename "$src")
    local dst="$2"
    local dstdir=$(dirname "$dst")

    if [[ ! -r "$src" ]]; then
        msg "Error: The source '$src' file not found"
        exit 2
    elif [[ -d "$dst" ]]; then
        msg "Error: Refusing to install as a directory"
        exit 3
    elif [[ -z "$src" ]] || [[ -z "$dst" ]]; then
        msg "Error Refusing to install an empty source '$src' or destination '$dst'"
        exit 4
    elif [[ "$srcname" =~ "$(basename $0)" ]]; then
        msg "Skipping installing the installer-script or similar file"
        return 0
    elif [[ "$src" =~ "~*~$" ]] || [[ "$dst" =~ "~*~$" ]]; then
        msg "Error: Encountered a backup source '$src' or destination '$dst'"
        exit 5
    elif [[ "$src" == $(truepath "$dst") ]]; then
        msg "Skipping install of duplicate link to '"$(truepath "$src")"'"
        return 0
    elif [[ ! -d "$dstdir" ]]; then
        mkdir -vp "$dstdir"
    fi
    echo -n "Installing link from " &> /dev/stderr
    ln --symbolic --verbose --backup=numbered "$src" "$dst"
}

cd $REPO_ROOT
msg "Installing configuration and Script files"
for DIR in $DIRS
do
    for relative_filepath in $(find $DIR -type f); do
        install_link $REPO_ROOT/$relative_filepath $HOME/$relative_filepath
    done
done

for DOTFILE in $DOTFILES; do
    install_link "$REPO_ROOT/$DOTFILE" "$HOME/.$DOTFILE"
done
