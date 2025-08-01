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
- Allows execution of Kali Default Impacket PsExec or WMIExec for PrivEsc or Access

## Installation & Execution

Install from Github

```sh
cd %DIRECTORY_of_your_choosing%
sudo git clone https://github.com/NEED-Programming/Golden-Ticket.git
sudo chmod +x golden_ticket.sh
```

Execution
```sh
./golden_ticket.sh
Follow the prompts
 -- Drops Administrator.ccache in CURRENT foler --
```

Cleanup
```sh
sudo rm -r domain_sid.txt && rm -r krbtgt_nt_hash.txt && rm -r Administrator.ccache
```


<img width="471" height="295" alt="golden_ticket" src="https://github.com/user-attachments/assets/83ac772e-e7dc-45b5-a408-5f934fe1de79" />


