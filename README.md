# Golden-Ticket
Creating them Golden Tickets
- Already Have Domain Admin?
- Want to create a Golden ticket but don't remember all the commands?
- Easy access?
- Post Exploit ✨Magic ✨

## Features

- Uses Netexec to Gather Domain SID
- Uses Netexec to dump NTDS for user 'krbtgt'
- Creation of a Golden ticket for the user 'Administrator'
- Exports Administrator ticket
- Allows execution of Impacket PsExec or WMIExec for PrivEsc or Access

## Installation & Execution

Install from Github

```sh
cd %DIRECTORY_of_your_choosing%
sudo git clone https://github.com/NEED-Programming/NeedServices.git
sudo chmod +x golden_ticket.sh
```

Execution
```sh
./golden_ticket.sh
Follow the prompts
```

Cleanip
```sh
sudo rm -r domain_sid.txt && rm -r krbtgt_nt_hash.txt && rm -r Administrator.ccache
```
