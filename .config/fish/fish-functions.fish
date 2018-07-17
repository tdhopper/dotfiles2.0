function subf
    code -n .
end

function subl
    code $argv
end

# Git commit alias
function gc
    git commit --verbose $argv
end


# Git push new branch to upstream
function gpo
    set -x CURRENT_BRANCH (git branch | awk '/^\* / { print $2 }')
    git push --set-upstream origin $CURRENT_BRANCH
end

# Explain shell command
function explain
    set -x arg (perl -MURI::Escape -le "print uri_escape('$argv')")
    open 'http://explainshell.com/explain?cmd='$arg
end

set --erase fish_greeting

function rsync_head
    rm -rf /tmp/(basename $PWD)
    git clone . /tmp/(basename $PWD)
    rm -rf /tmp/(basename $PWD)/.git
    rsync --archive --stats --rsh ssh /tmp/(basename $PWD) $1:$2
end
