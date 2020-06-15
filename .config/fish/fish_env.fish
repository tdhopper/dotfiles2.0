set --erase fish_greeting

set --global CDPATH . "~/n" "~/repos" "~" $CDPATH

source ~/.iterm2_shell_integration.(basename $SHELL)
register-python-argcomplete --shell fish pipx | .


set --global --export GOPATH (go env GOPATH)
set --global --export GOROOT (go env GOROOT)
set --global --export GOPRIVATE "github.com/nextmv-io/*"
set --global --export --append PATH $GOPATH/bin

set fish_key_bindings fish_user_key_bindings
status --is-interactive; and source (pyenv init -|psub)
