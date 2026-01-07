. ~/.config/fish/fish-functions.fish
. ~/.config/fish/fish-env.fish
. ~/.config/fish/fish-aliases.fish
. ~/.config/fish/fish-keybindings.fish

# Source secrets if the file exists
if test -f ~/.config/fish/secrets.fish
    . ~/.config/fish/secrets.fish
end
if test -e ~/.config/fish/fish-work.fish
   . ~/.config/fish/fish-work.fish
end
fish_add_path --move --path /opt/spotify-devex/bin
