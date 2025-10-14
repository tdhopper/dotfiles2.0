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

bind \cq '__park'

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

function cutbranch
    set -l branch $argv[1]
    set -l base $argv[2]

    if test -z "$branch"
        echo "usage: cutbranch <branch> [base]"
        return 1
    end

    if test -z "$base"
        set base "master"
    end

    # Resolve repo & default worktrees dir inside the repo under a .gitignored 'worktrees' directory
    set -l repo_root (git rev-parse --show-toplevel 2>/dev/null)
    if test $status -ne 0
        echo "cutbranch: Not in a git repository"
        return 1
    end

    # Refuse to run from inside a linked git worktree
    set -l git_dir (git rev-parse --git-dir 2>/dev/null)
    set -l git_common_dir (git rev-parse --git-common-dir 2>/dev/null)
    if test "$git_dir" != "$git_common_dir"
        echo "cutbranch: Refusing to run inside a git worktree at $repo_root. Run from the primary checkout." >&2
        return 2
    end

    set -l repo_name (basename "$repo_root")
    set -l worktrees_dir "$repo_root/worktrees"
    set -l worktree_path "$worktrees_dir/$branch"

    # Pre-create directory structure
    mkdir -p "$worktree_path/.vscode"

    # Ensure the 'worktrees/' path is ignored (do this in background if needed)
    if not git -C "$repo_root" check-ignore -q "worktrees/" 2>/dev/null
        if test -f "$repo_root/.gitignore"
            if not grep -qxF "worktrees/" "$repo_root/.gitignore"
                echo "worktrees/" >> "$repo_root/.gitignore"
            end
        else
            echo "worktrees/" >> "$repo_root/.git/info/exclude"
        end
    end

    # Create worktree directly from local branch (skip fetch if local exists)
    if git -C "$repo_root" show-ref --verify --quiet "refs/heads/$base"
        # Use local branch
        git -C "$repo_root" worktree add -B "$branch" "$worktree_path" "$base"
    else
        # Fetch only if we need to
        git -C "$repo_root" fetch -q origin "$base:$base" 2>/dev/null; or true
        git -C "$repo_root" worktree add -B "$branch" "$worktree_path" "$base"
    end

    # Calculate color outside of background job
    set -l color "#"(printf %s "$branch" | shasum | cut -c1-6)

    # Do setup work in parallel using background jobs
    fish -c "
        # Link the repo's virtualenv if it exists
        if test -d '$repo_root/.venv' -a ! -e '$worktree_path/.venv'
            ln -s '$repo_root/.venv' '$worktree_path/.venv'
        end

        # Create a unique VS Code/Cursor look for this worktree
        printf '{
  \"workbench.colorCustomizations\": {
    \"terminal.background\": \"#fff\",
    \"sideBar.background\": \"#fff\",
    \"window.activeBorder\": \"$color\",
    \"window.inactiveBorder\": \"$color\",
    \"titleBar.activeForeground\": \"$color\",
    \"titleBar.activeBackground\": \"$color\",
    \"activityBar.activeBorder\": \"$color\",
    \"statusBar.border\": \"$color\"
  },
  \"window.title\": \"$repo_name\${separator}$branch\"
}
' > '$worktree_path/.vscode/settings.json'
    " &

    # Open editor immediately (don't wait for setup to complete)
    if type -q cursor
        cursor "$worktree_path" &
    else if type -q code
        code "$worktree_path" &
    else
        echo "Open your editor at: $worktree_path"
    end

    # Wait for background setup to complete
    wait

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
