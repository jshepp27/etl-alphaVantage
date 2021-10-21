#!/bin/bash

unset DATABASE_URI
export DATABASE_URI="postgresql://huylpljjnoshbe:b51e90b80991f8e32ed4399a04c6db2a837f803995392e79472d1b92110ac60b@ec2-34-250-16-127.eu-west-1.compute.amazonaws.com:5432/dc7g7o62up02ai"
echo $DATABASE_URI

# don't forget to source your script prior to running!!! source envConfig.sh
# postgres://{user}:{password}@{hostname}:{port}/{database-name}