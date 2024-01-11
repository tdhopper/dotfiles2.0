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
