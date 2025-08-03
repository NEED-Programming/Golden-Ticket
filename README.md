# Golden-Ticket
Creating them Golden Tickets
- Already Have Domain Admin?
- Want to create a Golden ticket but don't remember all the commands?
- Easy access?

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
```

Execution
```sh
./golden_ticket.sh
Follow the prompts
 ### Drops Administrator.ccache in CURRENT folder ###
```

Cleanup
```sh
sudo rm -r domain_sid.txt && rm -r krbtgt_nt_hash.txt && rm -r Administrator.ccache
```


<img width="471" height="295" alt="golden_ticket" src="https://github.com/user-attachments/assets/83ac772e-e7dc-45b5-a408-5f934fe1de79" />

<iframe src="https://player.vimeo.com/video/1106493100?title=0&amp;byline=0&amp;portrait=0&amp;badge=0&amp;autopause=0&amp;player_id=0&amp;app_id=58479" width="1280" height="720" frameborder="0" allow="autoplay; fullscreen; picture-in-picture; clipboard-write; encrypted-media; web-share" referrerpolicy="strict-origin-when-cross-origin" title="Golden_Ticket"></iframe>

