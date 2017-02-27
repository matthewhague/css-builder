#!/bin/bash

PYTHON=pypy

for example in examples/*
do
    echo "Doing $example"
    $PYTHON main.py -s $example
done
