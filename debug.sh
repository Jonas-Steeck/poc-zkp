#!/bin/bash

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Attestation

cd $DIR/attestation

python3 attestation.py > $DIR/artifacts/witness-parameters.txt

cat $DIR/artifacts/witness-parameters.txt
echo " "
# Proving

cd $DIR/proving
zokrates compile -i poc.zok -o $DIR/artifacts/out --debug
compiledSize=$(du -kh $DIR/artifacts/out | cut -f1)

cat ../artifacts/witness-parameters.txt | xargs zokrates compute-witness -i $DIR/artifacts/out -o $DIR/artifacts/witness -a 
