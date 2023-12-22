#!/usr/bin/env bash

set -e
cd "$(dirname "$0")"
cd ..
export PYTHON_POD_LIST=`kubectl get pods -n data-tooling | grep colossal-ai | grep Running | awk '{ print $1 }' | grep -v NAME`
echo $PYTHON_POD_LIST


echo "$PYTHON_POD_LIST" | while IFS= read -r PYTHON_POD
do
    echo '====================='
    echo "Processing pod: $PYTHON_POD"


    file_list=()

    file_list+=($(git status -s | grep -v '^ *D' | cut -c 3-  | xargs ls -lt |  awk '{print $9}' | head -5 ))


    file_list+=(
    )

    echo ${file_list[@]}
    echo "==========================="

    for file in ${file_list[@]}; do
      file_folder=$(dirname $file)
      #echo kubectl cp -n data-tooling ./$file ${PYTHON_POD}:/workspace/${file_folder}/
      kubectl cp -n data-tooling ./$file ${PYTHON_POD}:/workspace/${file_folder}/
      echo $file
    done


    echo 'END' at $(date)

done
# kubectl cp exec-service-python-5f6947dc59-hhbtt:/home/ubix/app/del_summary.csv ./del_summary.csv

