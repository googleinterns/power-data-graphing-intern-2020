#!/bin/bash
# Sample data generator

#initial time
a=1577836800

# Output filename
file=Power_sample_data.csv


for loop in {1..7200000}
do
  time=$(($a+$loop))
  value=$((1 + RANDOM%100))
  echo $time,$value,SYSTEM >> $file
done
