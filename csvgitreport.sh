#!/bin/bash

#	C1-SP2	symphony-ivi-2.6.34_101105_1004510
#	C2-RC?	symphony-ivi-2.6.34_101206_1005018
#	C3	symphony-ivi-2.6.34_110206_1100652
#	C3-SP1	symphony-ivi-2.6.34_110305_1101068

mkdir -p /tmp/C3-SP1/diffs
mkdir -p /tmp/C3-SP1/change_logs

wget --quiet --no-parent --output-document=- \
	"http://ferret.mvista.com/Ferret/html/php/listCollections_dev.php?export&msd=symphony-ivi-2.6.34" | \
gawk -F ',' '
	BEGIN {
			system("echo")
			system("echo '=========='")
			system("echo 'U-Boot'")
			system("echo '=========='")
			system("echo")
			system("git --git-dir=/var/cache/git/gitosis_backups/bosch/uboot-ivi/.git log --reverse --pretty=format:%s C3..origin/2010-03/symphony-ivi-stabilize-C3")
			system("git --git-dir=/var/cache/git/gitosis_backups/bosch/uboot-ivi/.git diff -p C3 origin/2010-03/symphony-ivi-stabilize-C3 >/tmp/C3-SP1/diffs/U-Boot.C3_to_C3-SP1.diff 2>&1")
			system("git --git-dir=/var/cache/git/gitosis_backups/bosch/uboot-ivi/.git log --reverse --pretty --stat C3..origin/2010-03/symphony-ivi-stabilize-C3 >/tmp/C3-SP1/change_logs/U-Boot.C3_to_C3-SP1.txt 2>&1")
			system("echo")
	}
	/^IP/{
		split($0,header)
	}
	/symphony-ivi-2.6.34_110206_1100652/{
		fields=split($0, begin)
	}
	/symphony-ivi-2.6.34_110305_1101068/{
		split($0,end)
	}
	END {
		for (i = 1; i <= fields; i += 1) {
			if (header[i] == "Kernel") {
				header[i] = "Linux"
				repo = "/var/cache/git/kernel/mvlinux"
			} else if (header[i] == "symphony-ivi-gm" ||
				 header[i] == "symphony-ivi-cm" ||
				 header[i] == "symphony-ivi-platform" ||
				 header[i] == "symphony-ivi-simulator")
				repo = "/var/cache/git/mvl6/" header[i]
			else
				continue

			if (header[i] == "symphony-ivi-cm")
				begin[i] = "symphony-ivi-gm-1102020218"

			system("echo")
			system("echo '=========='")
			system("echo " header[i] ":")
			system("echo '=========='")
			system("echo")
			system("echo git --git-dir=" repo ".git log --reverse --pretty=format:%s " begin[i] ".." end[i])
			system("git --git-dir=" repo ".git log --reverse --pretty=format:%s " begin[i] ".." end[i])
			system("git --git-dir=" repo ".git diff -p " begin[i] " " end[i] " >/tmp/C3-SP1/diffs/" header[i] ".C3_to_C3-SP1.diff 2>&1")
			system("git --git-dir=" repo ".git log --reverse --pretty --stat " begin[i] ".." end[i] " >/tmp/C3-SP1/change_logs/" header[i] ".C3_to_C3-SP1.txt 2>&1")
			system("echo")

			if (header[i] == "Linux")
				continue

			system("echo")
			system("echo '=========='")
			system("echo " header[i] "-sources:")
			system("echo '=========='")
			system("echo")
			system("echo git --git-dir=" repo "-sources.git log --reverse --pretty=format:%s " begin[i] ".." end[i])
			system("git --git-dir=" repo "-sources.git log --reverse --pretty=format:%s " begin[i] ".." end[i])
			system("git --git-dir=" repo "-sources.git log --reverse --pretty --stat " begin[i] ".." end[i] " >/tmp/C3-SP1/change_logs/" header[i] "-sources.C3_to_C3-SP1.txt 2>&1")
			system("echo")
		}
	}'
