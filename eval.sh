#!/bin/bash

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Attestation

cd $DIR/attestation

python3 attestation.py > $DIR/artifacts/witness-parameters.txt


# Code compiling
cd $DIR/proving
START=`date +%s`
zokrates compile -i poc.zok -o $DIR/artifacts/out --debug
END=`date +%s`
compDur=$(echo "$END - $START" | bc)
compiledSize=$(du -kh $DIR/artifacts/out | cut -f1)

mv abi.json $DIR/artifacts/

# Zokrates setup
START=`date +%s`
zokrates setup -i $DIR/artifacts/out -p $DIR/artifacts/proving.key -v $DIR/artifacts/verification.key
END=`date +%s`
setupDur=$(echo "$END - $START" | bc)
provingKeySize=$(du -kh $DIR/artifacts/proving.key  | cut -f1)
verificationKeySize=$(du -kh $DIR/artifacts/verification.key | cut -f1)

# Witness generation
START=`date +%s`
cat ../artifacts/witness-parameters.txt | xargs zokrates compute-witness -i $DIR/artifacts/out -o $DIR/artifacts/witness -a 
END=`date +%s`
witnessDur=$(echo "$END - $START" | bc)


# Proof generation
START=`date +%s`
zokrates generate-proof -i $DIR/artifacts/out -j $DIR/artifacts/proof.json -p $DIR/artifacts/proving.key -w $DIR/artifacts/witness
END=`date +%s`
proofDur=$(echo "$END - $START" | bc)

# Verification
START=`date +%s%3N`
zokrates verify -v $DIR/artifacts/verification.key -j $DIR/artifacts/proof.json --verbose
END=`date +%s%3N`
verifyDur=$(echo "scale=0; $END - $START" | bc)

# Statistics
echo "Compilation: $compDur sec:" 
echo "Setup: $setupDur sec."
echo "Witness: $witnessDur sec."
echo "Proof: $proofDur sec."
echo "Verification: $verifyDur sec."
echo "Compiled size: $compiledSize"
echo "Proving key size: $provingKeySize"
echo "Verification key size: $verificationKeySize"