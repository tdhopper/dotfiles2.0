function .env
    python -m venv .env
    source ./.env/bin/activate.fish
end

function __park
    set --local cmd (commandline)
    set --local cursor (commandline --cursor)
    commandline --replace ""

    function __unpark --inherit-variable cmd --inherit-variable cursor --on-event fish_prompt
        functions --erase __unpark
        commandline --replace $cmd
        commandline --cursor $cursor
    end
end

function review_this_branch

    set -l base_branch $argv[1]

    if test -z "$base_branch"
        # Check if origin/main exists, otherwise fall back to origin/master
        if git rev-parse --verify origin/main >/dev/null 2>&1
            set base_branch "origin/main"
        else
            set base_branch "origin/master"
        end
    end
    # Check if the current branch is behind the base branch
    git fetch origin >/dev/null 2>&1
    set -l current_branch (git rev-parse --abbrev-ref HEAD 2>/dev/null)

    # Count how many commits the current branch is behind the base branch
    set -l behind_count (git rev-list --count $current_branch..$base_branch 2>/dev/null)

    if test "$behind_count" -gt 0
        echo -e "\033[33mWarning: Your branch is $behind_count commit(s) behind $base_branch.\033[0m"
        echo -e "\033[33mYou should consider updating your branch with:\033[0m"
        echo -e "\033[36m  git pull --rebase origin $base_branch\033[0m"
        echo ""
    end

    git fetch origin >/dev/null 2>&1
    set -l current_branch (git rev-parse --abbrev-ref HEAD 2>/dev/null)

    git diff $base_branch..$current_branch | llm -t code-review | glow
end

function pr-description
    set -l base_branch $argv[1]

    if test -z "$base_branch"
        # Check if origin/main exists, otherwise fall back to origin/master
        if git rev-parse --verify origin/main >/dev/null 2>&1
            set base_branch "origin/main"
        else
            set base_branch "origin/master"
        end
    end
    # Check if the current branch is behind the base branch
    git fetch origin >/dev/null 2>&1
    set -l current_branch (git rev-parse --abbrev-ref HEAD 2>/dev/null)

    # Count how many commits the current branch is behind the base branch
    set -l behind_count (git rev-list --count $current_branch..$base_branch 2>/dev/null)

    if test "$behind_count" -gt 0
        echo -e "\033[33mWarning: Your branch is $behind_count commit(s) behind $base_branch.\033[0m"
        echo -e "\033[33mYou should consider updating your branch with:\033[0m"
        echo -e "\033[36m  git pull --rebase origin $base_branch\033[0m"
        echo ""
    end

    git fetch origin >/dev/null 2>&1
    set -l current_branch (git rev-parse --abbrev-ref HEAD 2>/dev/null)

    git diff $base_branch..$current_branch | llm -t pr
end


function gcsflac2mp3
    if test (count $argv) -lt 2
        echo "Usage: gcsflac2mp3 <gs://bucket/file.flac> <output.mp3>"
        return 1
    end

    set input $argv[1]
    set output $argv[2]

    gsutil cp $input - | ffmpeg -i pipe:0 -f mp3 -b:a 320k $output
end

function claude
    if test -n "$SSH_CONNECTION" -a -z "$KEYCHAIN_UNLOCKED"
        security unlock-keychain ~/Library/Keychains/login.keychain-db
        set -gx KEYCHAIN_UNLOCKED true
    end
    command claude $argv
end
