rule MetadataTestRule
/*
    // These rule strings will match the rule strings below unmodified ...
    Testing $s4 = "for ssh_creds in ${allThreads[@]}; do" ascii fullword
    Testing $s8 = "allThreads=($1)" ascii fullword
    Testing $s9 = "$(host): encrypt files. Done." ascii fullword

    // These rule strings with some modifications match the rule strings below ...
    Testing $s1 = "echo -e "[-] Ping \033[31m${host_name}\033[0m bad"" ascii fullword
    Testing $s2 = ""${user_name}"@"${host_name}" -p "${port}" ascii fullword
    Testing $s3 = "'$password' &" <<< GMANcode27'" ascii fullword
    Testing $s5 = ""text=$MSG" "$MSG_URL$id&"" ascii fullword
    Testing $s6 = "--exclude=\*.☢ -l" fullword
    Testing $s7 = "--include=\*.{txt,sh,exe}" ascii fullword
*/
{
    strings:
        $s1 = "echo -e \"[-] Ping \\033[31m${host_name}\\033[0m bad\"" ascii fullword
        $s2 = "\"${user_name}\"@\"${host_name}\" -p \"${port}" ascii fullword
        $s3 = "'$password' &\" <<< GMANcode27'" ascii fullword
        $s4 = "for ssh_creds in ${allThreads[@]}; do" ascii fullword
        $s5 = "\"text=$MSG\" \"$MSG_URL$id&\"" ascii fullword
        $s6 = "--exclude=\\*.☢ -l" fullword
        $s7 = "--include=\\*.{txt,sh,exe}" ascii fullword
        $s8 = "allThreads=($1)" ascii fullword
        $s9 = "$(host): encrypt files. Done." ascii fullword

    condition:
        any of them
}
