#!/bin/sh

##################################################################
## Generates log file, tags and build RPM for CloudInit modules ##
##################################################################

if [ $# -lt 1 ]; then
        echo "Please insert your CERN username!"
        read -p "User:" USER
else
        USER=$1
fi


CURRENT_DIR=`pwd`
GIT_DIR=${CURRENT_DIR%/*}
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
if [ $GIT_BRANCH -ne "devel" ]; then
        echo "Attention: this script is meant to run on the devel branch. Exiting..."
        exit 3
fi

# Creating tag
# TODO : Allow passing the tag version as argument
echo "The current list of existing tags is:"
git tag -l

LAST_TAG=`git describe --abbrev=0`
echo "The last tag version is "$LAST_TAG
aux=1
while [ $aux ]
do
        read -p "What is the tag version that should be created?" TAG_VERSION
        if git show-ref --verify "refs/tags/${TAG_VERSION}"; then
                echo "That version already exists, please choose another or Ctrl+C to abort"
        else
                aux=0
        fi
done

# ChangeLog file
# git log --pretty=format:"%h - %an, %ar : %s" > FULL_LOG
echo "Writing CHANGELOG for new tag "$TAG_VERSION
echo "${TAG_VERSION} in "`date` > $GIT_DIR/CHANGELOG
git log --pretty=format:'  - %s' ${LAST_TAG}.. >> $GIT_DIR/CHANGELOG
read -p "Would you like to add/modify something in the CHANGELOG?y/n(other key)" ADD_CHANGELOG
if [ $ADD_CHANGELOG -eq 'y' || $ADD_CHANGELOG -eq 'Y' ]; then
        ${EDITOR:-vi} $GIT_DIR/CHANGELOG
fi

git add $GIT_DIR/CHANGELOG

git commit -a -s -m "$TAG_VERSION"

echo "Creating new tag: "$TAG_VERSION
git log --pretty=format:'  - %s' ${LAST_TAG}.. | git tag -a $TAG_VERSION -F -

git push --tags

echo "Tagging is done...Building a new RPM:"
# RPM building
# This file is supposed to be in the /etc/ directory. 
# If it is not, this will fail
if [ -f $GIT_DIR/rpm/cern-cloudinit-modules*.rpm ]; then
        RPM_NAME=`basename $GIT_DIR/rpm/cern-cloudinit* .noarch.rpm`
        CURRENT_REL=${RPM_NAME:${#RPM_NAME} - 1}
        echo "Current Release: "$CURRENT_REL
        NEW_REL=$CURRENT_REL+1
        echo "By default the new release will be: "$NEW_REL

        OLD_LINE='Release: 1'
        NEW_LINE='Release: '$NEW_REL

        SPEC_FILE_NAME=`basename cern*.spec`
        sed -i 's/'$OLD_LINE'/'$NEW_LINE'/g' $SPEC_FILE_NAME


        # TODO: Allow to modify the version
else
        if [ -f cern*.spec ]; then
                echo "There is no available RPM but there is a SPEC file.\n"
                echo "Current "`cat cern*.spec | grep Release`

        else
                echo "The RPM and respective SPEC file weren't found. Exiting script..."
                exit 3
        fi
fi






echo "To mount DFS you need to be root, please insert your root password below."

MOUNT_DIR='/tmp/dfs/cern.ch/'
mkdir -p $MOUNT_DIR
if [ $# -ge 2 ]; then
        PASS=$2
        # Ignore arguments that are not expected
        sudo mount -t cifs //cerndfs.cern.ch/dfs $MOUNT_DIR -o user=$USER,password=$PASS
else
        echo "You didn't provide your NICE password as an argument!"
        echo "This password is needed if you want to mount DFS. Please insert it now..."
        sudo mount -t cifs //cerndfs.cern.ch/dfs $MOUNT_DIR -o user=$USER
fi


echo "Unmounting DFS..."
sudo umount $MOUNT_DIR

exit 0
