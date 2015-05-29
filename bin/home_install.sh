#!/bin/bash

DOTFILES="astylerc bash_profile gitconfig vimrc"
DIRS="bin"

if ! [ -e "${PWD}/README.md" ] || ! [ -d "${PWD}/.git" ]
then
    echo "Script must be run from repository root"
    exit 1
fi

for DOTFILE in $DOTFILES
do
    if ! [ -e "${PWD}/${DOTFILE}" ]
    then
        echo "$DOTFILE not found: Script must be run from repository root"
        exit 2
    fi
    rm "${HOME}/.${DOTFILE}"
    ln -s "$(basename $PWD)/${DOTFILE}" "${HOME}/.${DOTFILE}"
done

for DIR in $DIRS
do
    if [ -e "${HOME}/${DIR}" ]
    then
        mv "${HOME}/${DIR}" "${HOME}/${DIR}.original"
    fi
    ln -s "$(basename $PWD)/${DIR}" "${HOME}/${DIR}"
done
