# Flexy Reader Public
A public repository which contains the shell script and python script to collect smart metrics from the Smart Meter

### Install Crontab task to send the metrics every minute
```sh
# checkout this repo
git clone https://github.com/Technology-lab/flexy-reader.git flexy-reader-public

# install python dependenies
pip3 install dsmr-parser requests jsons retrying

# create log file
touch /home/pi/flexy-reader-public/dsmr.log

# export variable $FLEXY_BACKEND_HOST to the system
echo 'export FLEXY_BACKEND_HOST=<API-URL>' >> ~/.bashrc

# edit crontab and add FLEXY_BACKEND_HOST env variable to override the api url and add entry to run the dsmr_reader_cron script every minute
crontab -l | { cat; echo "FLEXY_BACKEND_HOST=<API-URL> 
*/1 * * * * sh /home/pi/flexy-reader-public/dsmr_reader_cron.sh >> /home/pi/flexy-reader-public/dsmr.log 2>&1"; } | crontab -

# check the script logs 
tail -f /home/pi/flexy-reader-public/dsmr.log

# if something goes wrong
# check syslog
tail -f /var/log/syslog
# check auth log
tail -f /var/log/auth.log
```
