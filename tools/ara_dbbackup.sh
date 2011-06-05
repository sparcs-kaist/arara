#!/bin/sh
# ARAra DB Backup Utility
# Author: pipoket@sparcs.kaist.ac.kr
# Modifier: combacsa@sparcs.kaist.ac.kr
# Set necessary variables and run it.

CURR_DATE=`date +%y%m%d_%H%M%S`
BACKUP_FNAME=mysqlbackup_$CURR_DATE
BACKUP_PATH="."
BACKUP_REMOTE=""
BACKUP_REMOTE_PATH=""
DBNAME=""
DBUSER=""
DBPASS=""

echo "ARARA MySql Database Backup Script(v 0.1)"

if [ "$DBNAME" == "" ]; then
    echo "Error: You must specify DB Name in DB Backup Script."
    exit
fi

echo "Dumping mysql database to $BACKUP_PATH/$BACKUP_FNAME..."
mysqldump $DBNAME -u$DBUSER -p$DBPASS > $BACKUP_PATH/$BACKUP_FNAME

if [ "$BACKUP_REMOTE" == "" ]; then
    echo "No remote path is specified. Backup done."
else
    echo "SCPing dumped database to $BACKUP_REMOTE:$BACKUP_REMOTE_PATH..."
    scp $BACKUP_PATH/$BACKUP_FNAME $BACKUP_REMOTE:$BACKUP_REMOTE_PATH
fi

echo "Script finished!"
