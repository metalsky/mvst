#!/usr/bin/python
import sys, os, string, re
#******************************
# check that the patch numbers are in order
# August 30, 2006
# Annette Roll (help from Mike Harris)
##########################################

# function to determine missing patches
def getMissingPatches(num_patches, s_patches):
  # for each patch, check the curent patch value with the next next higher patch value
  # if the next patch value isn't 1 greater than the current patch value, print the 
  # current patch value + 1 through the next higher patch value - 1
  count = 0
  while count < num_patches - 1:
    current_patch = string.atoi(string.strip(s_patches[count]))
    next_patch = string.atoi(string.strip(s_patches[count + 1]))
    if current_patch + 1 != next_patch:
      patch_diff = next_patch - current_patch - 1
      while patch_diff > 0:
        current_patch += 1
        print "Missing patch " + str(current_patch)
        patch_diff -= 1
    count += 1



#Collect a list of patch files, make sure the total number of patches
#matches the patch number of the last file in the directory.
#
#Returns 1 on success, 0 on failure.
def checkPatches(path, debug=0):

  patchpath = path
  os.chdir(patchpath)

  #Collect the patch numbers, sort, and count.
  s_patches = os.popen("find | grep .mvlpatch | awk -F - {'print $2'}").readlines()
  s_patches.sort()
  num_patches = len(s_patches)

  # If the first patch + number of patches != highest patch number, fail.  Else succeed.
  if string.atoi(s_patches[0]) + (num_patches - 1) != string.atoi(s_patches[num_patches - 1]):
    if debug:
      print "\npatches out of sequence, determining missing patches..."
      getMissingPatches(num_patches, s_patches)
      return 0
    else:
      return 0
  else:
    if debug:
      print "\npatches in sequnce, no missing patches"
      print "first patch value is %s" % string.strip(s_patches[0])
      print "last patch value is %s" % string.strip(s_patches[num_patches - 1])
      print "number of patches is %s" % num_patches
      print
      return 1
    else:
      return 1


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: %s %s" % (sys.argv[0], "<patch path>")
    sys.exit(1)
  checkPatches(sys.argv[1], debug=1)
