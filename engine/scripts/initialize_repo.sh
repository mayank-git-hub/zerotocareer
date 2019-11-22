base_dir='/home/mayank/temporary_git_repos/'$1
git_repo=$1.
git_repo_url=https://git.zerotocareer.com/$git_repo
base_code=/home/Common/GitRepos/new/zerotocareer/engine/scripts/template_code/main.py

cd $base_dir
git pull origin https://root:root1@git.zerotocareer.com/$1.git
cp  $base_dir ./
git add .
git commit -m __init__
git push origin master 