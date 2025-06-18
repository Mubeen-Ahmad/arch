import os, json, time, requests, subprocess, pyperclip
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.console import Console
from rich.table import Table

# ==== CONFIG ====
REPO = "watchlist"
GITHUB_USER = "Mubeen-Ahmad"
EMAIL = "Mubeenahmad1199@gmail.com"
SSH_DIR = os.path.expanduser("~/.ssh")
KEY_PATH = os.path.join(SSH_DIR, f"id_rsa_{REPO}")
CONFIG_PATH = os.path.join(SSH_DIR, "config")
ssh_host = f"github-{REPO}"
console = Console()

# ==== UTILS ====
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table(data):
    table = Table(show_header=True, header_style="bold red")
    if not data:
        console.print("[bold yellow]No data found.[/bold yellow]")
        return
    for key in data[0].keys():
        table.add_column(key.capitalize(), style="green")
    for item in data:
        table.add_row(*[str(item.get(col, "")) for col in item])
    console.print(table)

def read_json():
    if os.path.exists("data.json"):
        with open("data.json", "r") as f:
            return json.load(f)
    return []

def write_json(data):
    with open("data.json", "w") as fw:
        json.dump(data, fw, indent=4)

def show_data():
    data = read_json()
    print_table(data)

def add_data():
    fields = {
        "Name": "Enter Name",
        "Genre": "e.g Fantasy | Action ...",
        "Type": "Episode / Movie",
        "Status": "Watch / Watched",
        "Code": "Unique Code"
    }
    for k, v in fields.items():
        user = input(f"\033[92m{k}\033[0m ({v}): ")
        fields[k] = user
    data = read_json()
    uid = max([int(i.get('uid')) for i in data if i.get('uid')], default=0) + 1
    fields["uid"] = str(uid)
    data.append(fields)
    write_json(data)

def edit():
    key = input("Enter UID to edit: ")
    data = read_json()
    for item in data:
        if item['uid'] == key:
            for k in list(item.keys()):
                if k != "uid":
                    user = prompt(f"{k}: ",default=item[k])
                    # user = input(f"{k} ({item[k]}): ")
                    if user:
                        item[k] = user
            write_json(data)
            return
    console.print("[red]UID not found![/red]")

def delete():
    key = input("Enter UID to delete: ")
    data = read_json()
    new_data = [i for i in data if i['uid'] != key]
    if len(data) != len(new_data):
        write_json(new_data)
        console.print("[green]Deleted successfully.[/green]")
    else:
        console.print("[red]UID not found![/red]")

# def filter_by_code():
#     code = input("Enter Code to filter: ")
#     data = read_json()
#     filtered = [i for i in data if i['Code'] == code]
#     print_table(filtered)


def filter_by_code():
    # code = input("Enter Code to filter by: ")
    totalfield = ['Type', 'Status', 'Code']
    console.print(f"[bold green]Select Option :> {' | '.join(totalfield)}[/bold green]")
    field = input("")
    if field in totalfield: 
        # ---------------------------------------------------
        data = read_json()
        tmp = []
        
        if data:
            
            if field != "Code":
                check_field = []
                for i in data:
                    for k,v in i.items():
                        if i.get(field) not in check_field:
                           check_field.append(i.get(field))
                            
                console.print(f"[bold green]Select Field :> {' | '.join(check_field)}[/bold green]")
                user=input("")
                clear()
                if user in check_field:
                    
                    for i in data:
                        if i[field] == user:
                            tmp.append(i)
                
                    
                else:
                    console.print(f"[bold red]Invalid Input[/bold red]")
                print_table(tmp)

            else:
                tmp = []
                show_data()
                console.print(f"[bold green]Enter Code[/bold green]")
                user=input("")
                for i in data:
                    if i["Code"] == user:
                        tmp.append(i)
                clear()
                print_table(tmp)
                    
                
            # ---------------------------------------------------
    else:
        console.print(f"[bold red]Invalid Input[/bold red]")
        clear()

def copykey():
    if os.name != 'nt':
        with open(f"{KEY_PATH}.pub") as f:
            console.print("[cyan]Copy the Key[/cyan]")
            console.print(f"[green]\n\n{f.read()}\n\n[/green]")
    else:            
        with open(f"{KEY_PATH}.pub") as f:
            pyperclip.copy(f.read())
            console.print("[cyan]SSH key copied to clipboard![/cyan]")

def repodata():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/data.json"
    response = requests.get(url)
    data = response.json()
    print_table(data)

def pullrepodata():
    url = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO}/main/data.json"
    response = requests.get(url)
    write_json(response.json())

def push():
    def run(cmd):
        return subprocess.run(cmd, shell=True).returncode == 0
    run("git init .")
    run("git add data.json")
    run(f'git config --global user.name "{GITHUB_USER}"')
    run(f'git config --global user.email "{EMAIL}"')
    run("git branch -M main")
    if not os.path.exists(KEY_PATH):
        run(f'ssh-keygen -t rsa -b 4096 -f "{KEY_PATH}" -N "" -C "{REPO}@github"')
        
        if os.name != 'nt':
            with open(f"{KEY_PATH}.pub") as f:
                console.print("[cyan]Copy the Key[/cyan]")
                console.print(f"[green]\n\n{f.read()}\n\n[/green]")
                console.print(f"[green][Press Enter after adding key to GitHub][/green]")
                input()
        else:  
            with open(f"{KEY_PATH}.pub") as f:
                pyperclip.copy(f.read())
                
            console.print(f"[green][Press Enter after adding key to GitHub][/green]")
            
    host_block = f"""
Host {ssh_host}
    HostName github.com
    User git
    IdentityFile {KEY_PATH.replace(os.sep, '/')}
    IdentitiesOnly yes
"""
    os.makedirs(SSH_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_PATH) or ssh_host not in open(CONFIG_PATH).read():
        with open(CONFIG_PATH, "a") as f:
            f.write(host_block)
    run("ssh-keyscan github.com >> ~/.ssh/known_hosts")
    run("git remote remove origin || echo skipping")
    run(f"git remote add origin git@{ssh_host}:{GITHUB_USER}/{REPO}.git")
    run("git commit -am 'update' || echo no changes to commit")
    if not run("git push -u origin main"):
        run("git pull --rebase origin main")
        run("git push -u origin main")

# ==== HACKER PANEL MENU ====
def print_menu():
    #console.print("\n[bold green]━━━━━━━━━━━━━━━ HACKER PANEL ━━━━━━━━━━━━━━━[/bold green]")
    console.print("\n[bold red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold red]")
    console.print("[cyan][●] show        [●] add         [●] edit      [/cyan]")
    console.print("[cyan][●] delete      [●] filter      [●] repodata  [/cyan]")
    console.print("[cyan][●] pull        [●] push        [●] copykey   [/cyan]")
    console.print("[cyan][●] exit[/cyan]")
    console.print("[bold red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold red]")

# ==== MAIN ====
def main():
    clear()
    options = ['show', 'add', 'edit', 'filter', 'repodata', 'pull', 'push', 'copykey', 'delete', 'exit']
    completer = WordCompleter(options, ignore_case=True)
    cli_style = Style.from_dict({ '': '#00ff00 bold' })

    while True:
        print_menu()
        try:
            user = prompt(HTML("<ansiyellow>> </ansiyellow>"), completer=completer, style=cli_style).strip()
        except (KeyboardInterrupt, EOFError):
            break
        clear()
        if user == 'exit': break
        elif user == 'show': show_data()
        elif user == 'add': show_data(); add_data(); clear(); show_data()
        elif user == 'edit': show_data(); edit(); clear(); show_data();
        elif user == 'delete': show_data(); delete(); clear(); show_data()
        elif user == 'filter': show_data(); filter_by_code()
        elif user == 'copykey': copykey()
        elif user == 'repodata': console.print("[bold cyan]Local Data:[/bold cyan]"); show_data(); console.print("\n[bold cyan]Repo Data:[/bold cyan]"); repodata()
        elif user == 'pull': pullrepodata()
        elif user == 'push': console.print("[green]Pushing...[/green]"); push(); clear();
        else:
            console.print("[bold red]Invalid Option[/bold red]")

if __name__ == "__main__":
    main()
