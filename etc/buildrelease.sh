#!/bin/sh

##################################################################
## Generates log file, tags and build RPM for CloudInit modules ##
##################################################################

usage () {
	echo "USAGE: ./buildrelease.sh [OPTIONS]=value"
	echo -e '\nScript to tag and build a new release for the CloudInit modules.\n'
	echo -e 'OPTIONS:\n'
	echo -e '  --h\tHelp. Prints this output.'
	echo -e '  --user\tSpecify the username of who is running the script. The same username that will be used to mount DFS.'
	echo -e '  --tag\tName of the tag that will be created.'
	echo -e '  --repo_dir\tDirectory where the RPM will be uploaded to (DFS by default).'
	echo -e '  --code_url\tURL of the modules, where the RPM should fetch from.'  
}

USER=""
TAG_VERSION=""
REPO_DIR=""
CODE_URL=""

# Check for arguments
while [ $# -ge 1 ]; do
        case $1 in
                --h ) usage
                exit 1 ;;
                --user=* ) USER=${1#*=}; shift;;
                --tag=* ) TAG_VERSION=${1#*=}; shift;;
                --repo_dir=* ) REPO_DIR=${1#*=}; shift;;
                --code_url=* ) CODE_URL=${1#*=}; shift;;
                -* ) usage
                echo "Unrecognised options will be discarded." 
		exit 1;;
                * ) break ;;
        esac
done
#----#

if [ -z "$USER" ]; then
        echo "You must specify an username. Please insert your CERN username!"
        read -p "User:" USER
fi

echo "Welcome "$USER

CURRENT_DIR=`pwd`
GIT_DIR=${CURRENT_DIR%/*}
GIT_BRANCH=`git rev-parse --abbrev-ref HEAD`
if [ $GIT_BRANCH != "devel" ]; then
        echo "Attention: this script is meant to run on the devel branch. Changing..."
        git checkout devel
fi

# Creating tag
echo "The current list of existing tags is:"
git tag -l

LAST_TAG=`git describe --abbrev=0`
echo "The last tag version is "$LAST_TAG
aux=0
if [ ! -z "$TAG_VERSION" ]; then
	git show-ref --verify --quiet "refs/tags/${TAG_VERSION}"
        if [ $? -eq 0 ]; then
        	echo "That version already exists, please choose another or Ctrl+C to abort"
      		aux=1
	fi
fi
if [ $aux -eq 1 -o -z "$TAG_VERSION" ]; then
	while [ $aux ]
	do
        	read -p "What is the tag version that should be created?" TAG_VERSION
		git show-ref --verify --quiet "refs/tags/${TAG_VERSION}"
        	if [ $? -eq 0 ]; then
                	echo "That version already exists, please choose another or Ctrl+C to abort"
        	else
			break;
        	fi
	done
fi


# ChangeLog file
# git log --pretty=format:"%h - %an, %ar : %s" > FULL_LOG
echo "Writing CHANGELOG for new tag "$TAG_VERSION
echo "${TAG_VERSION} in "`date` > $GIT_DIR/CHANGELOG
git log --pretty=format:'  - %s' ${LAST_TAG}.. >> $GIT_DIR/CHANGELOG
read -p "Would you like to add/modify something in the CHANGELOG?y/n(other key)" ADD_CHANGELOG
if [ $ADD_CHANGELOG -eq 'y' ] || [ $ADD_CHANGELOG -eq 'Y' ]; then
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
if [ -f cern*.spec ]; then
        echo "Current "`cat cern*.spec | grep Release`
	CURRENT_REL=`cat cern*.spec | grep Release | awk '{print $2}'`
else
        echo "The SPEC file wasn't found. Exiting script..."
        exit 3
fi

NEW_REL=$TAG_VERSION

echo "The new release will be: "$NEW_REL

OLD_LINE='Release: '$CURRENT_REL
NEW_LINE='Release: '$NEW_REL
NEW_LINE=`echo $NEW_LINE | sed -e 's/-//g'` 
 
SPEC_FILENAME=`basename cern*.spec`
sed -i "s/${OLD_LINE}/${NEW_LINE}/g" $SPEC_FILENAME

OLD_VERSION='Version: '
NEW_VERSION='Version: '`echo ${TAG_VERSION:0:1}`
sed -i "s/${OLD_VERSION}.*/${NEW_VERSION}/g" $SPEC_FILENAME

OLD_CHECKOUT='git checkout '
NEW_CHECKOUT="git checkout ${TAG_VERSION}"
sed -i "s/${OLD_CHECKOUT}.*/${NEW_CHECKOUT}/g" $SPEC_FILENAME

if [ ! -z "$CODE_URL" ]; then
	#TODO
	NEW_URL=$CODE_URL
fi

# TODO : Allow RPM signing
rpmbuild -bb $GIT_DIR/etc/$SPEC_FILENAME --define "_rpmdir ."
if [ $? -ne 0 ]; then
	error=$?
        sed -i 's/'$NEW_LINE'/'$OLD_LINE'/g' $SPEC_FILENAME
        echo "You don't have the means to build a valid RPM."
        echo "Please check if you have rpm-build installed."
        echo "Exiting..."
        exit $error
fi

git add $SPEC_FILENAME 
      
mv -f noarch/cern*.rpm $GIT_DIR/rpm/
rm -fr noarch/

git rm -rf $GIT_DIR/rpm/repodata/

echo "New RPM was created. Creating repodata..."
createrepo $GIT_DIR/rpm/

echo "Ready to upload new data to website!"

echo "To mount DFS you need to be root, please insert your root password below."

if [ -z "$REPO_DIR" ]; then
	REPO_DIR='/tmp/dfs/cern.ch/'
fi

MOUNT_DIR=$REPO_DIR

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

NEW_REL_NAME=`echo $NEW_REL | sed -e 's/-//g'`

cp -fr $GIT_DIR/rpm/repodata/ $MOUNT_DIR'Websites/c/cern-cloudinit-modules/'
cp -f $GIT_DIR/rpm/cern*$NEW_REL_NAME.noarch.rpm $MOUNT_DIR'Websites/c/cern-cloudinit-modules/'

echo "Unmounting DFS..."
sudo umount $MOUNT_DIR

cd $GIT_DIR/rpm/
git add *
git commit -m "Adding RPM built from buildrelease script, on tag ${TAG_VERSION}"
git push

echo "Finished. Bye!"

exit 0
