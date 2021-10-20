#!/bin/bash

unset DATABASE_URI
export DATABASE_URI="postgresql://joshua.sheppard:Window5224@localhost/etl-alphaVantage"
echo $DATABASE_URI

# don't forget to source your script prior to running!!! source envConfig.sh
# postgres://{user}:{password}@{hostname}:{port}/{database-name}