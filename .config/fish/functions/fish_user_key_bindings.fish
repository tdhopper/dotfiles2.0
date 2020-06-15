function fish_user_key_bindings
    fish_vi_key_bindings
    bind -M insert \cf accept-autosuggestion
    bind -M insert -m default jj backward-char force-repaint
    for mode in insert default visual
      bind -M $mode \ck 'history --merge ; up-or-search'
      bind -M $mode \cj 'history --merge ; down-or-search'
    end
end