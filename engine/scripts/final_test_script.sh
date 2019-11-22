base_dir='/home/mayank/temporary_git_repos/'$1
cur_dir='/home/Common/GitRepos/new/zerotocareer/engine/scripts'
git_repo=$1.
git_repo_url=https://git.zerotocareer.com/$git_repo
base_code=/home/Common/GitRepos/new/zerotocareer/engine/scripts/template_code/main.py

cd $base_dir
git pull origin master

result1=$(python main.py test_case_1 2 3)
result2=$(python main.py test_case_2 4)
result3=$(python main.py test_case_3 5 6)

python $cur_dir'/collect_test_results.py' $2 result1 result2 result3 