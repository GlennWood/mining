_miners_script()
{
  local cur
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "$(python /opt/mining/etc/miners_bash_completion.py $(printf " %s" "${COMP_WORDS[@]}") )" -- ${cur}) )
  return 0
}
complete -F _miners_script miners
