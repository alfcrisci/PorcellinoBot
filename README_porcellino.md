# local launch

cd /home/porcellino

python porcellino_bot.py

# instable launch

cd /home/porcellino

nohup python porcellino_bot.py


# instance a daemon from root dir 

cp porcellino.conf /etc/init/porcellino.conf

# start demone

sudo start porcellino

# follow what happens (in another window) with:

tail -f /var/tmp/porcellino.log

# and stop with:

sudo stop porcellino


cd /home/porcellino
python porcellino_bot.py


pymeteosalute library's source https://github.com/alfcrisci/PyMeteoSalute



