_script()
{
  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "$(/opt/mining/etc/miners_bash_completion.py $(printf " %s" "${COMP_WORDS[@]}") )" -- ${cur}) )

  return 0
}
complete -F _script miners
