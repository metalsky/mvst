set scrolloff=3
set title
set wildmenu
set commentstring=\ #\ %s
set shiftwidth=4
set background=dark
set autoindent
syntax enable
"au BufWinLeave * mkview
"au BufWinEnter * silent loadview
set foldlevel=200
"map <f2> :w\|!python %<cr>
if has("autocmd")
autocmd FileType python set complete+=k/home/rell/pydiction/pydiction iskeyword+=.,(
endif