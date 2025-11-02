rule SuspiciousMacro
{
    strings:
        $macro = "AutoOpen"
        $powershell = "powershell"
        $wscript = "WScript.Shell"
    condition:
        any of them
}

rule CredentialHarvest
{
    strings:
        $url = "login"
        $phish = "verify your account"
    condition:
        $url and $phish
}

