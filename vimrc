version 6.0

if &cp | set nocp | endif
let s:cpo_save=&cpo
set cpo&vim
map! <xHome> <Home>
map! <xEnd> <End>
map! <S-xF4> <S-F4>
map! <S-xF3> <S-F3>
map! <S-xF2> <S-F2>
map! <S-xF1> <S-F1>
map! <xF4> <F4>
map! <xF3> <F3>
map! <xF2> <F2>
map! <xF1> <F1>
map <xHome> <Home>
map <xEnd> <End>
map <S-xF4> <S-F4>
map <S-xF3> <S-F3>
map <S-xF2> <S-F2>
map <S-xF1> <S-F1>
map <xF4> <F4>
map <xF3> <F3>
map <xF2> <F2>
map <xF1> <F1>
let &cpo=s:cpo_save
unlet s:cpo_save
set backspace=2
set fileencodings=utf-8,latin1
set fo=ql
set helplang=en
set history=50
set hlsearch
set ignorecase
set ruler
set smarttab
set termencoding=utf-8
set viminfo='20,\"50
set ts=4
set sw=4
set nosta
set sts=4
set et
set noai
set nosi
set spf="$HOME/.vimwords"
set title
set bg=dark
hi ExtraWhitespace ctermbg=darkgreen
autocmd FileType go setlocal noet
match ExtraWhitespace /\s\+\%#\@<!$/
match ExtraWhitespace /\s\+$\| \+\ze\t/
autocmd InsertLeave * redraw!
let c_space_errors = 1
let python_space_errors = 1
" match ExtraWhitespace /^.\{79\}.*$/
au BufRead,BufNewFile control set filetype=python
set rtp+=$GOROOT/misc/vim
filetype plugin indent on
syntax on
