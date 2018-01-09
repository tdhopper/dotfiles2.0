test -e {$HOME}/.iterm2_shell_integration.fish ; and source {$HOME}/.iterm2_shell_integration.fish

set --global CDPATH . "~/c" "~/repos" "~" $CDPATH
set --global --export PATH $PATH "/Users/thopper/Applications/Visual Studio Code.app/Contents/Resources/app/bin/"

function hi
    cowsay hi
end

function c
    cd ~/c
end

function subf
    subl -n .
end


function gc
    git commit --verbose $argv
end

# Git push new branch to upstream
function gpo
    set -x CURRENT_BRANCH (git branch | awk '/^\* / { print $2 }')
    git push --set-upstream origin $CURRENT_BRANCH
end

# pip fish completion start
function __fish_complete_pip
    set -lx COMP_WORDS (commandline -o) ""
    set -lx COMP_CWORD (math (contains -i -- (commandline -t) $COMP_WORDS)-1)
    set -lx PIP_AUTO_COMPLETE 1
    string split \  -- (eval $COMP_WORDS[1])
end
complete -fa "(__fish_complete_pip)" -c pip
# pip fish completion end
