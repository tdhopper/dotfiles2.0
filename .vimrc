" Set 'nocompatible' to ward off unexpected things that your distro might
" have made, as well as sanely reset options when re-sourcing .vimrc
set nocompatible

" Attempt to determine the type of a file based on its name and possibly its
" contents. Use this to allow intelligent auto-indenting for each filetype,
" and for plugins that are filetype specific.
filetype indent plugin on

" Enable syntax highlighting
syntax on

" Display line numbers on the left
:set number relativenumber
:set nu rnu

" Key bindings
let mapleader = " "  " Sets the <leader> key to space

" Map Y to act like D and C, i.e. to yank until EOL, rather than act as yy,
" which is the default
map Y y$

" Commenting with <leader>c in visual mode
xnoremap <leader>c :Commentary<CR>

" Change with black hole register in normal mode (doesn't pollute clipboard)
nnoremap <leader>c "_c

" Escape mappings in insert mode
inoremap jk <Esc>
inoremap <Esc> <Nop>

" Disable arrow keys in insert mode
inoremap <Up> <Nop>
inoremap <Down> <Nop>
inoremap <Left> <Nop>
inoremap <Right> <Nop>

" Undo with u in normal mode
nnoremap u :undo<CR>

" Use system clipboard
set clipboard=unnamedplus

" Editor rulers
set colorcolumn=88

" Render control characters
set listchars=tab:>-,trail:·,extends:>,precedes:<,nbsp:+
set list

" Vim leader key bindings
nnoremap <leader>r :registers<CR>
nnoremap <leader>d "_dd

" Highlight yanked text
au TextYankPost * silent! lua vim.highlight.on_yank {higroup="IncSearch", timeout=150, on_visual=true}

" Disable cursor line and word wrapping
set nocursorline
set nowrap

" EasyMotion
let g:EasyMotion_do_mapping = 0  " Disable default mappings
" Add custom EasyMotion mappings here

" Trailing spaces
au BufWritePre * %s/\s\+$//e  " Trim trailing whitespace on save

" Accessibility and Zen Mode settings - Not applicable in Vim

" Better command-line completion
set wildmenu

" Show partial commands in the last line of the screen
set showcmd

" Highlight searches (use <C-L> to temporarily turn off highlighting; see the
" mapping of <C-L> below)
set hlsearch

" Use case insensitive search, except when using capital letters
set ignorecase
set smartcase

" Allow backspacing over autoindent, line breaks and start of insert action
set backspace=indent,eol,start

" When opening a new line and no filetype-specific indenting is enabled, keep
" the same indent as the line you're currently on. Useful for READMEs, etc.
set autoindent

" Stop certain movements from always going to the first character of a line.
" While this behaviour deviates from that of Vi, it does what most users
" coming from other editors would expect.
set nostartofline

" Display the cursor position on the last line of the screen or in the status
" line of a window
set ruler

" Always display the status line, even if only one window is displayed
set laststatus=2

" Instead of failing a command because of unsaved changes, instead raise a
" dialogue asking if you wish to save changed files.
set confirm

" Use visual bell instead of beeping when doing something wrong
set visualbell

" And reset the terminal code for the visual bell. If visualbell is set, and
" this line is also included, vim will neither flash nor beep. If visualbell
" is unset, this does nothing.
set t_vb=

" Specify a directory for plugins
" - For Neovim: stdpath('data') . '/plugged'
" - Avoid using standard Vim directory names like 'plugin'
call plug#begin('~/.vim/plugged')

Plug 'prabirshrestha/asyncomplete.vim'
Plug 'prabirshrestha/vim-lsp'
Plug 'prabirshrestha/asyncomplete-lsp.vim'

if executable('pyls')
    " pip install python-language-server
    au User lsp_setup call lsp#register_server({
        \ 'name': 'pyls',
        \ 'cmd': {server_info->['pyls']},
        \ 'allowlist': ['python'],
        \ })
endif
" Initialize plugin system
call plug#end()
