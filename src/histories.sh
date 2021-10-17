#!/bin/zsh

hist_type='zsh'
#hist_type='bash'

output_name=zsh-hist-rebuilt

# copy said history files to local place preserving timestamps and the like
target_dir=~/backup/histories/pulled/$hist_type/
echo $target_dir
#exit
mkdir -p $target_dir

function search_drives_for_histfiles () {
	#search drives for history files
	volumes=()
	for volume in $volumes; do
		sudo find /media/$username/volume/ -iname '.zsh_history' > ~/backup/histories/
	done
}

function copy_histfiles_from_drives () {
	for hist_file in $(cat "$hist_type"_history_files*); do
		echo processing $hist_file
		new_hist_file="$(echo $hist_file | sed 's/\//!/g')"
		echo new hist file $new_hist_file
		sudo cp -a "$hist_file" $target_dir"$new_hist_file"
	done
}

function load_histfiles_to_db () {
	# TODO first backup db file to backups dir in case histfiles pollute DB with broken
	# ie. single line instead of multiline commands or other corruptions

	cd $target_dir

	for hist_file in $(ls *"$hist_type"_history); do
		echo backing up to db: $hist_file
		head ./"$hist_file"
		# TODO add interactive accepting of this file
		zsh-hist.py -p ./"$hist_file" -d $target_dir/$output_name.db -m 10000000 -b
	done
}

function regenerate_histfile_from_db () {
	# TODO - first copy target histfile to another location if it exists
	# TODO - first run backup to temp database (in /tmp)
	rm /tmp/$output_name
	zsh-hist.py -p /tmp/$output_name -d $target_dir/$output_name.db -m 10000000 -r
	
}

load_histfiles_to_db
#regenerate_histfile_from_db
