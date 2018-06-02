_script()
{
  local cur prev
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "$(/opt/mining/install/install_miners.py bash_completion $(printf " %s" "${COMP_WORDS[@]}") )" -- ${cur}) )

  return 0
}
complete -F _script /opt/mining/install/InstallMiners.py
