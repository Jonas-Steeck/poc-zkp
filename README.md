# general-zkp
# POC

## Use Case  
A company want to create a ZKP to prove their carbon emissions.
  
To guarantee of the input values, they have to be signed by an auditor.  
In this POC the auditor can be anyone. The public key used to sign the values has to be used as an input.  
The formular to calcutate the carbon emissions used is

$$finalValue = \sum (carbonProductValue * recipeWeight)$$  

## Requirements
You will need to have docker installed.  

## Setup  

The input.json has all the inputs that are being used for the proof generation.  
Currently those include the recipe with the weights for each carbon value.  
The other fields are the carbon footprint values.  
There are also two arrays: pcfMaterialIds and recipeMaterialIds.  
They have to be the same and assure that only PCF values are used for the corresponding weights and no arbitrary signed values can be used.  

