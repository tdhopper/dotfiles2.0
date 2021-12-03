set fish_key_bindings fish_user_key_bindings
bind u history-search-backward
bind \cr history-search-forward
bind '[' history-token-search-backward
bind ']' history-token-search-forward
bind -M insert \cp history-search-backward
bind -M insert \cn history-search-forward
bind -M insert \cf accept-autosuggestion