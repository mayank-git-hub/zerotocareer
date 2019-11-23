# Cloning the repository in a temporary folder, copying the template code and then commiting under the root user credentials

base_dir='/home/mayank/temporary_git_repos/'
git_repo=$1.
git_repo_url=https://git.zerotocareer.com/$git_repo
base_code=/home/Common/GitRepos/new/zerotocareer/engine/scripts/template_code/main.py

cd $base_dir
echo "got into base dir "$base_dir
git clone https://root:root1@git.zerotocareer.com/$1.git
echo "cloned repo "$1
cd $1
echo "got into repo "$1
cp  $base_code ./
git add .
git commit -m __init__
git push origin master 