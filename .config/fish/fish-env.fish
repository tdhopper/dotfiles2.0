# Fish setup
set --erase fish_greeting

# pipx
set PATH $PATH ~/.local/bin
if test -q
    register-python-argcomplete --shell fish pipx | .
end

# Pyenv initialize
if type -q pyenv
    status --is-interactive; and source (pyenv init -|psub)
end

# Setup iterm2 shell iterm2_shell_integration
test -e {$HOME}/.iterm2_shell_integration.fish; and source {$HOME}/.iterm2_shell_integration.fish

# Quick CD
set --global CDPATH . "~/dtn" "~/repos" "~" $CDPATH

# Add VS Code to Path
set --global --export PATH $PATH ~/Applications/Visual\ Studio\ Code.app/Contents/Resources/app/bin/

# Pip autocomplete
function __fish_complete_pip
    set -lx COMP_WORDS (commandline -o) ""
    set -lx COMP_CWORD (math (contains -i -- (commandline -t) $COMP_WORDS)-1)
    set -lx PIP_AUTO_COMPLETE 1
    string split \  -- (eval $COMP_WORDS[1])
end
complete -fa "(__fish_complete_pip)" -c pip

# Direnv enable
function __direnv_export_eval --on-event fish_postexec;
        "/usr/local/bin/direnv" export fish | source;
end

set -x MANPAGER "sh -c 'col -bx | bat -l man -p'"
