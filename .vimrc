:syntax on

" Enable vim to jump to the last position when reopening a file
if has("autocmd")
  au BufReadPost * if line("'\"") > 0 && line("'\"") <= line("$")
    \| exe "normal! g'\"" | endif
endif

set tabstop=2 shiftwidth=2 expandtab

let &colorcolumn = join(range(81,999), ",")
highlight ColorColumn ctermbg=235 guibg=#2c2d27

function! FormatFile()
  write
  setlocal autoread
  if (&ft == "python")
    silent execute "!yapf -i " . bufname("%")
  elseif (&ft == "cmake")
    silent execute "!cmake-format -i " . bufname("%")
  else
    silent execute "!clang-format -i " . bufname("%")
  endif
  redraw!
  edit
endfunction

function! HeaderToggle()
  let file_path = expand("%")
  let file_name = expand("%<")
  let extension = split(file_path, '\.')[-1]
  let err_msg = "There is no file "

  if (extension == "c") || 
\    (extension == "cpp") || 
\    (extension == "cc") || 
\    (extension == "cxx")
    for ext in ["h", "hpp"]
      let next_file = join([file_name, ext], ".")

      if filereadable(next_file)
        execute ":e %<." . expand(ext)
        return
      endif
    endfor
    echo "No header file found"
  elseif (extension == "h") ||
\        (extension == "hpp")
    for ext in ["c", "cpp", "cc", "cxx"]
      let next_file = join([file_name, ext], ".")

      if filereadable(next_file)
         execute ":e %<." . expand(ext)
        return
      endif
    endfor
    echo "No implementation file found"
  endif
endfunction

let mapleader=","
nnoremap <leader>h :call HeaderToggle()<cr>
nnoremap <leader>cf :call FormatFile()<cr>
