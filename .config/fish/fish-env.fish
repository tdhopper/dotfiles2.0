
function add_to_path_if_exists
    set -l dir $argv[1]
    if test -d $dir
        fish_add_path $dir
    else
        echo "Directory '$dir' does not exist."
    end
end

function source_if_exists
    set -l file $argv[1]
    if test -f $file
        source $file
    else
        echo "File '$file' does not exist."
    end
end

set --global CDPATH . "~/c" "~/repos" "~" $CDPATH

add_to_path_if_exists /opt/homebrew/bin
add_to_path_if_exists ~/.local/bin
source_if_exists {$HOME}/.iterm2_shell_integration.fish


# Pip autocomplete
function __fish_complete_pip
    set -lx COMP_WORDS (commandline -o) ""
    set -lx COMP_CWORD (math (contains -i -- (commandline -t) $COMP_WORDS)-1)
    set -lx PIP_AUTO_COMPLETE 1
    string split \  -- (eval $COMP_WORDS[1])
end
complete -fa "(__fish_complete_pip)" -c pip

if type -q direnv
    function __direnv_export_eval --on-event fish_postexec;
            direnv export fish | source;
    end
end

starship init fish | source

string match -q "$TERM_PROGRAM" "vscode"
and . (code --locate-shell-integration-path fish)
