import scan_git
import requests
import questionary

def find_repositories():
    search_choice = questionary.select(
        "Search by:",
        choices=["User name", "Organization name", "exit"]
    ).ask()
    if search_choice == "User name":
        print("user")
        user = input("please write the user you want to search for: \n")
        list_repositories = requests.get("{}/users/{}/repos".format(url, user), headers=headers)
        if list_repositories.status_code == 200:
            return user
        else:
            print(f" Failed to fetch repos: {list_repositories.status_code}")
            print(list_repositories.text)
            return None

    elif search_choice == "Organization name":
        print("orgs")
        user = input("please write the organization you want to search for: \n")
        list_repositories = requests.get("{}/orgs/{}/repos".format(url, user), headers=headers)
        if list_repositories.status_code == 200:
            return user
        else:
            print(f" Failed to fetch repos: {list_repositories.status_code}")
            print(list_repositories.text)
            return None
    else:
        return None
def describe_repositories(user = None):
        list_repositories = requests.get("{}/users/{}/repos".format(url, user),headers=headers)
        if list_repositories.status_code == 200:
            listed_repositories = []
            for i in list_repositories.json():
                listed_repositories.append(i["name"])

            listing_repo = questionary.select(
                    "Choose action:",
                    choices=listed_repositories
                ).ask()
            issues_repository = requests.get("{}/repos/{}/{}/issues".format(url,user,listing_repo),headers=headers)
            issues_only = [issue for issue in issues_repository.json() if 'pull_request' not in issue]
            commit_message = requests.get("{}/repos/{}/{}/commits".format(url,user,listing_repo),headers=headers)
            pull_requests = requests.get("{}/repos/{}/{}/pulls".format(url,user,listing_repo),headers=headers)
            for i in list_repositories.json():
                if listing_repo == (i["name"]):
                    print(f"Repository name: {i['name']}"
                            f"\nDescription: {i['description']}"
                            f"\nOpen Issues: {len(issues_only)}"
                            f"\nLast Push: {i['pushed_at']}"
                            f"\nCommit message: {commit_message.json()[0]['commit']['message']}"
                            f"\nPull requests:  {len(pull_requests.json())}"
                            f"\nClone: git clone {i['clone_url']}")
                    return listing_repo,len(issues_only),len(pull_requests.json())
            else:
                print(f" Failed to fetch repos: {list_repositories.status_code}")
                print(list_repositories.text)
                return 0,0,0

def inspect_issues(user = None):
    issues_repository = requests.get("{}/repos/{}/{}/issues".format(url, user, listing_repo), headers=headers)
    issues_only = [issue for issue in issues_repository.json() if 'pull_request' not in issue]

    for issue in issues_only:
        open_issues.append({
            "name": f"{issue['number']}: {issue['title']}",
            "value": issue['number']})
    manage_issues = questionary.select(
        "Choose an issue:",
        choices=open_issues
    ).ask()
    get_issues_repository = requests.get("{}/repos/{}/{}/issues/{}".format(url, user, listing_repo,manage_issues), headers=headers)
    issue_get = get_issues_repository.json()
    print("\n--- Issue Details ---")
    print(f"Title      : {issue_get.get('title')}")
    print(f"Number     : {issue_get.get('number')}")
    print(f"User       : {issue_get.get('user', {}).get('login')}")
    print(f"State      : {issue_get.get('state')}")
    print(f"Created at : {issue_get.get('created_at')}")
    print(f"Updated at : {issue_get.get('updated_at')}")
    print(f"Labels     : {[label['name'] for label in issue_get.get('labels', [])]}")
    print(f"\nBody:\n{issue_get.get('body')}\n")

    close_issue = questionary.select(
        "Do you want to close this issue?:",
        choices=["Yes", "No"]
    ).ask()

    issue_json = {
        'state': 'closed'
    }
    if close_issue == "Yes":
        closing_issue = requests.patch("{}/repos/{}/{}/issues/{}".format(url, user, listing_repo, manage_issues),
                                             headers=headers,json=issue_json)
        if closing_issue.status_code == 200:
            print(closing_issue)
            print(f"{listing_repo} was closed")
        else:
            print("Closing the issue wasn't allowed ")


def inspect_pull_requests(user = None):
    pull_requests = requests.get("{}/repos/{}/{}/pulls".format(url, user, listing_repo), headers=headers)
    for pull_request in range(len(pull_requests.json())):
        open_pull_requests.append({
                "name": f"{pull_requests.json()[pull_request]['number']}: {pull_requests.json()[pull_request]['title']}",
                "value": pull_requests.json()[pull_request]['number']})
    manage_pull_requests = questionary.select(
        "Choose an a pull requests:",
        choices=open_pull_requests
    ).ask()

    get_issues_repository = requests.get("{}/repos/{}/{}/pulls/{}".format(url, user, listing_repo, manage_pull_requests),headers=headers)
    pull_get = get_issues_repository.json()

    print("\n--- Pull Request Details ---")
    print(f"Title         : {pull_get.get('title')}")
    print(f"Number        : {pull_get.get('number')}")
    print(f"User          : {pull_get.get('user', {}).get('login')}")
    print(f"State         : {pull_get.get('state')}")
    print(f"Created at    : {pull_get.get('created_at')}")
    print(f"Updated at    : {pull_get.get('updated_at')}")
    print(f"Merged        : {pull_get.get('merged')}")
    print(f"Mergeable     : {pull_get.get('mergeable')}")
    print(f"Merge Status  : {pull_get.get('mergeable_state')}")
    print(f"Draft         : {pull_get.get('draft')}")
    print(f"\nBody:\n{pull_get.get('body')}\n")

    approve_pull_request = questionary.select(
        "Do you approve this pull request?:",
        choices=["Yes","No"]
    ).ask()
    if approve_pull_request == "Yes":
        closed_pull_request = requests.put("{}/repos/{}/{}/pulls/{}/merge".format(url, user, listing_repo, manage_pull_requests),headers=headers)
        if closed_pull_request.status_code == 200:
            print(closed_pull_request)
            print(f"{listing_repo} was approved for merging")
        else:
            print("Merging wasn't allowed ")


url = "https://api.github.com"

try:
    with open("my_secret_git_key.txt") as token_file:
        headers = {
            "Authorization": f"token {token_file.read().strip()}"

    # with open("git_key.txt") as token_file:
    #     headers = {
    #         "Authorization": f"token {token_file.read().strip()}"
        }
except FileNotFoundError:
    print("Token file not found.")
    exit(1)


stop_menu = False


while not stop_menu :

    management_options = ['Exit']
    open_issues = []
    open_pull_requests = []



    main_menu = questionary.select(
        "Hello, please choose an action :",
        choices=["Search and describe repositories","Search for secrets","exit"]
    ).ask()

    if main_menu == "Search and describe repositories":
        user =  find_repositories()
        listing_repo, len_issues ,len_pull_requests = describe_repositories(user = user)
        if len_issues > 0:
            management_options.append('Check issues')
        if len_pull_requests > 0:
            management_options.append('Check pull requests')
        if len(management_options) > 1:
            manage_repo = questionary.select(
                "Choose action for your chosen repository:",
                choices=management_options
            ).ask()
            if manage_repo == 'Check issues':
                inspect_issues(user)
            elif manage_repo == 'Check pull requests':
                inspect_pull_requests(user)

    elif  main_menu == "Search for secrets":
        print("hi")
    else:
        stop_menu = True