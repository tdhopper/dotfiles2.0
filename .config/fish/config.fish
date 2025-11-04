set -U fish_greeting ""
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

# pnpm
set -gx PNPM_HOME "/Users/thopper/Library/pnpm"
if not string match -q -- $PNPM_HOME $PATH
  set -gx PATH "$PNPM_HOME" $PATH
end
# pnpm end
