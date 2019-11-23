# Self explainatory code

base_dir='/home/mayank/temporary_git_repos/'$1
cur_dir='/home/Common/GitRepos/new/zerotocareer/engine/scripts'
git_repo=$1.
git_repo_url=https://git.zerotocareer.com/$git_repo
base_code=/home/Common/GitRepos/new/zerotocareer/engine/scripts/template_code/main.py

cd $base_dir
git pull origin master

result1=$(python main.py test-case-1 --var1 2 --var2 3)
result2=$(python main.py test-case-2 --var1 4)
result3=$(python main.py test-case-3 --var1 5 --var2 6)
result4=$(python main.py test-case-1 --var1 5 --var2 10)
result5=$(python main.py test-case-2 --var1 5)
result6=$(python main.py test-case-3 --var1 5 --var2 4)

if [[ $result1 == "" ]]
then
	result1=None
fi

if [[ $result2 == "" ]]
then
	result2=None
fi

if [[ $result3 == "" ]]
then
	result3=None
fi

if [[ $result4 == "" ]]
then
	result4=None
fi

if [[ $result5 == "" ]]
then
	result5=None
fi

if [[ $result6 == "" ]]
then
	result6=None
fi

echo $result1 $result2 $result3;

python $cur_dir'/collect_test_results.py' $2 "final" $result1 $result2 $result3 $result4 $result5 $result6