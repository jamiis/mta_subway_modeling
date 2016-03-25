# this script takes around an hour to download all data 
# should be augmented to be async in the future
mkdir data
mkdir info

wget --accept txt,xls \
     --mirror \
     --progress=dot \
     --adjust-extension \
     --convert-links \
     --backup-converted \
     --no-parent \
     http://web.mta.info/developers/turnstile.html

mv web.mta.info/developers/data/nyct/turnstile/* data
mv web.mta.info/developers/resources/nyct/turnstile/* info
rm -rf web.mta.info

# make sure you sudo apt-get install catdoc
xls2csv info/Remote-Booth-Station.xls > info/Remote-Booth-Station.csv
