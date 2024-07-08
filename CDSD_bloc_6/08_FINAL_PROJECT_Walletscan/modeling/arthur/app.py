import ethereum
print('Should be False:',ethereum.check_checksum('ff'))
print('Should be True:',ethereum.check_checksum('0x9b22a80d5c7b3374a05b446081f97d0a34079e7f'))
print('Should be True:',ethereum.check_checksum('0x4838B106FCe9647Bdf1E7877BF73cE8B0BAD5f97'))