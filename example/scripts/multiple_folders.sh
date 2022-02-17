# Script to parse multiple target folders #
# Do not modify script!!
#
# >> Enter python environment and copy script to another place to use
#

target_folders=("folder_1" "folder_1" "folder_1")
for ((i=0; i < ${#target_folders[@]}; i++ )); do
python main.py -c "data/${target_folders[$i]}/config.json";
done
sleep 5
