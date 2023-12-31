# Runs tests by ID from cli params.

Import-Module "~/AtomicRedTeam/invoke-atomicredteam/Invoke-AtomicRedTeam.psd1" -Force

for ( $i = 0; $i -lt $args.count; $i++ ) {
	write-host "Starting $($args[$i])"
	Get-Date -UFormat "%A %m/%d/%Y %R %Z"
	Invoke-AtomicTest $args[$i] -GetPreReqs
	Invoke-AtomicTest $args[$i]
	Invoke-AtomicTest $args[$i] -CleanUp
}

write-host "Completed $($args.count) tests. sleeping 10."
Start-Sleep -Seconds 10
