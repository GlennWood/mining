_miners_installer_script()
{
  local cur
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "$(python /opt/mining/install/InstallMiners.py bash_completion $(printf " %s" "${COMP_WORDS[@]}") )" -- ${cur}) )
  return 0
}
complete -F _miners_installer_script InstallMiners.py
