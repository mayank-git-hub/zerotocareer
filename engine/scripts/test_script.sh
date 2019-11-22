base_dir='/home/mayank/temporary_git_repos/'$1
cur_dir='/home/Common/GitRepos/new/zerotocareer/engine/scripts'
git_repo=$1.
git_repo_url=https://git.zerotocareer.com/$git_repo
base_code=/home/Common/GitRepos/new/zerotocareer/engine/scripts/template_code/main.py

cd $base_dir
git pull origin master

result1=$(python main.py test-case-1 --var1 1 --var2 2)
result2=$(python main.py test-case-2 --var1 1)
result3=$(python main.py test-case-3 --var1 2 --var2 3)

if [[ $result1 == "" ]]
then
	result1=3
fi

if [[ $result2 == "" ]]
then
	result2=None
fi

if [[ $result3 == "" ]]
then
	result3=None
fi

echo $result1 $result2 $result3;

python $cur_dir'/collect_test_results.py' $2 "" $result1 $result2 $result3 