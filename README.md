# Golden-Ticket
Creating them Golden Tickets
- Already Have Domain Admin?
- Want to create a Golden ticket but don't remember all the commands?
- Easy access?

<img width="471" height="295" alt="golden_ticket" src="https://github.com/user-attachments/assets/83ac772e-e7dc-45b5-a408-5f934fe1de79" />

<img width="804" height="180" alt="image" src="https://github.com/user-attachments/assets/b186ccc6-73c7-476b-9da6-362619efad60" />


## Features

- Uses Netexec to Gather Domain SID
- Uses Netexec to dump NTDS for user 'krbtgt'
- Creation of a Golden ticket for the user 'Administrator'
- Exports Administrator ticket
- Allows execution of Kali Default Impacket PsExec, WMIExec, SMBExec, and ATExec for Post Exploit ✨Magic ✨

## Installation & Execution

Install from Github

```sh
cd %DIRECTORY_of_your_choosing%
sudo git clone https://github.com/NEED-Programming/Golden-Ticket.git
sudo chmod +x golden_ticket.sh
or
sudo chmod +x golden_ticket.py
```

Execution
```sh
./golden_ticket.sh
or
pythom3 golden_ticket.py
Follow the prompts
 ### Drops Administrator.ccache in CURRENT folder ###
```

Cleanup
```sh
sudo rm -r domain_sid.txt && rm -r krbtgt_nt_hash.txt && rm -r Administrator.ccache 
or
sudo rm -r Administrator.ccache && rm -r run_impacket.sh
```

## Video
https://vimeo.com/1106493100
