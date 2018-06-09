_miners_installer_script()
{
  local cur
  COMPREPLY=()
  cur="${COMP_WORDS[COMP_CWORD]}"
  COMPREPLY=( $(compgen -W "$(python3 /opt/mining/etc/install_miners_bash_completion.py $(printf " %s" "${COMP_WORDS[@]}") )" -- ${cur}) )
  return 0
}
complete -F _miners_installer_script InstallMiners
