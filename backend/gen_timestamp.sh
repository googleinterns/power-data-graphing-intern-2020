#!/bin/bash
# Sample data generator

#initial time
a=1566950884158711

# Output filename
file=Power_sample_data.csv 


for loop in {1..7200000}
do
  time=$(($a+1000*$loop))
  value=$((1 + RANDOM%100))
  echo $time,$value,SYSTEM >> $file
done
