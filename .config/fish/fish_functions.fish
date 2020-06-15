# Git push new branch to upstream
function gpo
    set -x CURRENT_BRANCH (git branch | awk '/^\* / { print $2 }')
    git push --set-upstream origin $CURRENT_BRANCH
end

