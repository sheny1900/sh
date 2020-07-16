#!/bin/bash
# re_pwd 修改的目录
re_pwd=$1 
# 需要进行修改的格式
# .c .cpp .h .java .cpp .cc .i
re_type=$2

function main(){
find $re_pwd/ -name *.$re_type | while read i
do 
	echo "$i";
	cat $i  > $i.txt
#	rm -rvf $i
done
}

main $1 $2
