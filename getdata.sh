# this script takes around an hour to download all data 
# from the MTA on a slow coffee shop connection
mkdir data
mkdir info

wget --accept txt,xls 
     --mirror 
     --progress=dots 
     --adjust-extension 
     --convert-links 
     --backup-converted 
     --no-parent
     http://web.mta.info/developers/turnstile.html

mv web.mta.info/developers/data/nyct/turnstile/* data
mv web.mta.info/developers/resources/nyct/turnstile/* info
rm -rf web.mta.info
