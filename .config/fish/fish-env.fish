set -U fish_greeting ""

function add_to_path_if_exists
    set -l dir $argv[1]
    if test -d $dir
        fish_add_path $dir
    end
end

function source_if_exists
    set -l file $argv[1]
    if test -f $file
        source $file
    end
end

set --global CDPATH . "~/repos" "~" $CDPATH

add_to_path_if_exists /opt/homebrew/bin
add_to_path_if_exists /usr/local/bin
add_to_path_if_exists ~/.local/bin
add_to_path_if_exists ~/.lmstudio/bin
add_to_path_if_exists ~/Library/pnpm
source_if_exists ~/.cargo/env.fish
source_if_exists {$HOME}/.iterm2_shell_integration.fish

if type -q direnv
    direnv hook fish | source
end

if type -q starship
    starship init fish | source
end
