import hashlib
import os
from bitstring import BitArray
from zokrates_pycrypto.eddsa import PrivateKey, PublicKey
from zokrates_pycrypto.field import FQ
from zokrates_pycrypto.utils import write_signature_for_zokrates_cli, pprint_for_zokrates
import struct
import sys
import json
import pprint

verbose = not os.getenv('PROD', default=None)

def vprint(msg: str = "", pretty=False):
    if verbose:
        if pretty:
            pprint.pprint(msg)
        else:
            print(msg)

# Returns R, S, M0, M1
def write_signature_for_zokrates_cli(sig, msg):
    "Writes the input arguments for verifyEddsa in the ZoKrates stdlib to file."
    sig_R, sig_S = sig
    args = [sig_R.x, sig_R.y, sig_S]
    args = " ".join(map(str, args))

    M0 = msg.hex()[:64]
    M1 = msg.hex()[64:]

    #u0 = [str(int(M0[i:i+8], 16)) for i in range(0,len(M0), 8)]
    #u1 = [str(int(M1[i:i+8], 16)) for i in range(0,len(M1), 8)]
    # b0 = BitArray(int(M0, 16).to_bytes(32, "big")).bin
    # b1 = BitArray(int(M1, 16).to_bytes(32, "big")).bin
    args = args # + " " + " ".join(u0 + u1)

    return args


def publicKey_to_string(publicKey: PublicKey) -> str:
    return str(publicKey.p.x.n) + " " + str(publicKey.p.y.n)

def createFootprintOutput(value: int, materialId: int, privateKey: PrivateKey = None):
    """
    Takes a carbon footprint value as input,
    returns a list of strings formatted as zokrates inputs:
    1. raw value in bytes
    2. signature parameters
    3. publicKey
    """
    if not privateKey:
        privateKey = PrivateKey.from_rand()
    
    publicKey = PublicKey.from_private(privateKey)

    bytesValue = int.to_bytes(value, 64, 'big')

    bytesMaterialId = int.to_bytes(materialId , 64, 'big')

    hashedValue = hashlib.sha256(bytesValue).digest()\
                + hashlib.sha256(bytesMaterialId).digest()
    
    bytesTotal = bytesValue + bytesMaterialId

    signedValue = privateKey.sign(hashedValue)

    rawFormattedValue = " ".join([str(i) for i in struct.unpack(">32I", bytesTotal)])

    formattedSignature = write_signature_for_zokrates_cli(signedValue, hashedValue)

    formattedPublicKey = publicKey_to_string(publicKey)

    return rawFormattedValue, formattedSignature, formattedPublicKey

def parseRecipe(array):

    bytesValues = b''
    for item in array:
        bytesValues += int.to_bytes(item, 4, 'big')

    bufferlength = 16 - len(array)
    bytesValues += int.to_bytes(0, 4, 'big') * bufferlength

    hashedValue = hashlib.sha256(bytesValues).digest()

    rawFormattedValue = " ".join([str(i) for i in struct.unpack(">16I", bytesValues)])

    return rawFormattedValue, hashedValue

# def parseRecipe(array):
#     # Hashing the recipe multiple times, therefor buffering it up to 156 values. 
#     # Then splitting it into chunks of 16 values and hasing them like a merkle tree


#     array.extend([0 for _ in range(256 - len(array))])
#     bytesArray = []
#     for i in range(16):
#         bytesFormatted = b''
#         for item in array[i*16:(i+1)*16]:
#             bytesFormatted += int.to_bytes(item, 4, 'big')
#         bytesArray.append(bytesFormatted) 

#     bytesValues = b''
#     for item in bytesArray:
#         bytesValues += item

#     rawValues = " ".join([str(i) for i in struct.unpack(">256I", bytesValues)])

#     while len(bytesArray) > 1:
#         helpArray = bytesArray
#         bytesArray = []
#         for i in range(len(helpArray)//2):
#             hash1 = hashlib.sha256(helpArray[i*2]).digest()
#             hash2 = hashlib.sha256(helpArray[i*2+1]).digest()
#             bytesArray.append(hash1+hash2)

#     return rawValues, bytesArray[0]


def createRecipeOutput(recipe:list, materialIds: list, arrayLength, privateKey: PrivateKey = None):

    if not privateKey:
        privateKey = PrivateKey.from_rand()
    
    if arrayLength <= 16:
        return createRecipeOutputFor1(recipe, materialIds, privateKey=privateKey)
    
    if len(recipe) % 16 != 0:
        bufferAmount = 16 - len(recipe)%16
        recipe.extend([0 for _ in range(bufferAmount)])
        materialIds.extend([0 for _ in range(bufferAmount)])

    raw = signed =  pkey = ""
    for i in range(arrayLength//16 + 1):
        newRaw, newSigned, newPkey = createRecipeOutputFor1(
            recipe[i*16:(i+1)*16],
            materialIds[i*16:(i+1)*16],
            privateKey=privateKey
        )
        raw = " ".join([raw, newRaw])
        signed = " ".join([signed, newSigned])
        pkey = " ".join([pkey, newPkey])
    
    return raw, signed, pkey
        

def createRecipeOutputFor1(recipe: list, materialIds: list, privateKey: PrivateKey = None):
    
    """
    Signes a hash that is created from 
    """
    if not privateKey:
        privateKey = PrivateKey.from_rand()
    
    publicKey = PublicKey.from_private(privateKey)

    rawRecipe, hashRecipe = parseRecipe(recipe)

    rawMaterialIds, hashMaterialIds = parseRecipe(materialIds)

    hashedValue = hashRecipe + hashMaterialIds

    signedValue = privateKey.sign(hashedValue)

    rawFormattedValue = rawRecipe + " " + rawMaterialIds

    formattedSignature = write_signature_for_zokrates_cli(signedValue, hashedValue)

    formattedPublicKey = publicKey_to_string(publicKey)

    vprint(rawFormattedValue+', '+  str(len(rawFormattedValue.split(' '))))

    return rawFormattedValue, formattedSignature, formattedPublicKey

def createFootprintOutputs(inputJson, length):

    rawPCFs, signedPCFs, auditorPCFs = "","",""

    for i, (pcf, materialId) in enumerate(zip(inputJson.get("pcfValues"), inputJson.get('pcfMaterialIds'))):

        rawPCF, signedPCF, auditorPCF = createFootprintOutput(pcf, materialId)

        rawPCFs = " ".join([rawPCFs, rawPCF])
        signedPCFs = " ".join([signedPCFs, signedPCF])
        auditorPCFs = " ".join([auditorPCFs, auditorPCF])

        if i + 1 == length:
            break

    for _ in range(length - len(inputJson.get('pcfValues'))):
        rawPCF, signedPCF, auditorPCF = createFootprintOutput(0, 0)

        rawPCFs = " ".join([rawPCFs, rawPCF])
        signedPCFs = " ".join([signedPCFs, signedPCF])
        auditorPCFs = " ".join([auditorPCFs, auditorPCF])


    return rawPCFs, signedPCFs, auditorPCFs


def main():
    
    arrayLengths = 3

    fileDir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(fileDir, "..", "inputs.json"), "r") as f:
        inputJson = json.load(f)
        vprint(inputJson, pretty=True)

    rawRecipe, signedRecipe, auditorRecipe = createRecipeOutput(inputJson.get('recipeWeights'), inputJson.get('recipeMaterialIds'), arrayLengths)

    rawPCFs, signedPCFs, auditorPCFs = createFootprintOutputs(inputJson, arrayLengths)

    stringOutput = " ".join([
        rawRecipe,
        signedRecipe,
        auditorRecipe,
        rawPCFs,
        signedPCFs,
        auditorPCFs
    ])

    sys.stdout.write(f"{stringOutput}")
    vprint()


def test():
    recipe = [i for i in range(17)]
    test = parseRecipe(recipe)
    print(test)

if __name__ == "__main__":
    main()
    #test()

