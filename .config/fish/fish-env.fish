# Setup conda
for conda_path in "$HOME/anaconda/bin" "$HOME/miniconda/bin" "$HOME/miniconda2/bin"
    if test -d $conda_path
        set -gx PATH $PATH $conda_path
        source (conda info --root)/etc/fish/conf.d/conda.fish
    end
end
#



# Setup iterm2 shell iterm2_shell_integration
test -e {$HOME}/.iterm2_shell_integration.fish ; and source {$HOME}/.iterm2_shell_integration.fish


# Quick CD
set --global CDPATH . "~/c" "~/repos" "~" $CDPATH

# Add VS Code to Path
set --global --export PATH $PATH "~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/"


# pip fish completion start
function __fish_complete_pip
    set -lx COMP_WORDS (commandline -o) ""
    set -lx COMP_CWORD (math (contains -i -- (commandline -t) $COMP_WORDS)-1)
    set -lx PIP_AUTO_COMPLETE 1
    string split \  -- (eval $COMP_WORDS[1])
end
complete -fa "(__fish_complete_pip)" -c pip
# pip fish completion end
