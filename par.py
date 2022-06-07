from __future__ import print_function
import json
import requests
import time

# Same information on bitcoin.conf file
rpcport = 18332
rpcuser = 'Chocolatier'
rpcpassword = 'RPCs'
rpcip = '127.0.0.1'
# ------------------------------------------------------------------------------------------------

# This is the informarion from above compliled to allow a local request to be made
serverURL = 'http://' + str(rpcuser) + ':' + str(rpcpassword)+ '@' + str(rpcip)+":" + str(rpcport)
#--------------------------------------------------------------------------------------------------

# This catches errors in the conection that might be encountered
class RPCHost(object):
    def __init__(self, url):
        self._session = requests.Session()
        self._url = url
        self._headers = {'content-type': 'application/json'}
    def call(self, rpcMethod, *params):
        payload = json.dumps({"method": rpcMethod, "params": list(params), "jsonrpc": "2.0"})
        tries = 5
        hadConnectionFailures = False
        while True:
            try:
                response = self._session.post(self._url, headers=self._headers, data=payload)
            except requests.exceptions.ConnectionError:
                tries -= 1
                if tries == 0:
                    raise Exception('Failed to connect for remote procedure call.')
                hadFailedConnections = True
                print("Couldn't connect for remote procedure call, will sleep for five seconds and then try again ({} more tries)".format(tries))
                time.sleep(10)
            else:
                if hadConnectionFailures:
                    print('Connected for remote procedure call after retry.')
                break
        if not response.status_code in (200, 500):
            raise Exception('RPC connection failure: ' + str(response.status_code) + ' ' + response.reason)
        responseJSON = response.json()
        if 'error' in responseJSON and responseJSON['error'] != None:
            raise Exception('Error in RPC call: ' + str(responseJSON['error']))
        return responseJSON['result']
# -------------------------------------------------------------------------------------------------------------------------------------

# This makes the request/call to the local Bitcoin Core with the information entered in the 2 previous steps
host = RPCHost(serverURL)
# -------------------------------------------------------------------------------------------------------------------------------------

# This makes a call requesting the latest known block on your local Bitcoin Core
latest_block= host.call('getblockcount')
print(latest_block)
# -------------------------------------------------------------------------------------------------------------------------------------

# In this example I want to search from the 'latest block' all the way down to block 710000, just to round it off.
while latest_block > 710000:

    # We need the blockhash and all the inforamtion contained in each block. That's what the next two steps accomplish
    get_block_hash= host.call('getblockhash',latest_block)
    #print(get_block_hash)
    block= host.call('getblock',get_block_hash,2)
    #print(block)
    # ----------------------------------------------------------------------------------------------------------------

    # Element tx contains the information of all transaction IDs in the block we are searching.
    transactions = block['tx']
    #print(transactions)
    # ----------------------------------------------------------------------------------------------------------------

    # Loop through all the information in 'transactions' (the previous variable) using the variable 'txid' as shown below.
    for txid in transactions:

        # We are going to search for each address and it's value, at the same time skip through any errors we might find.
        # Be ready for a bunch of addresses to print on your screen. If you want to skip this, comment out line 85.
        # You guys are programmers so obviously I did not need to add the above example.
        try:
            value=txid['vout'][0]['value']
            address=txid['vout'][0]['scriptPubKey']['address']
            address=address.replace( '[','')
            address=address.replace(']','')
            address=address.replace('\'','')
            print(str(address)+"'\t"+str(value))
            
            # ---------------------------------------------------------------------------------------------------------
            # Each loop below this line must be uncommented one section at a time. For example you can do a search for
            # a specific address, any addresses with a certain value, any address with a range value etc. But each ran
            # one at a time.

            # ---------------------------------------------------------------------------------------------------------
            # If you want to search for a specific address, just run a loop as follows:
            # Let's use a random address found on block 719834
            
            #if address == "bc1pelm7ze0nkvh8px2xwswzcc28zhklqlxuquwuuva7yw5txz0n3enqzgz5w6":
            #    print(str(address)+"'\t"+str(value))
            #    get_block_hash, blockhash, transactions, block, txid = 0, 0, 0, 0, 0
            #    latest_block = 0
            #else:
            #    get_block_hash, blockhash, transactions, block, txid = 0, 0, 0, 0, 0
            #    continue
            # -----------------------------------------------------------------------------------------------------------

            # In this following loop I want to see any addresses that have 6.25 Bitcoins in them.
            #if value == 6.25:

                # Print the results on the screen. If you don't want to see them just comment this bottom line out.
                #print(str(address)+"'\t"+str(value))
                # ------------------------------------------------------------------------------------------------------

                # This next step creates a .csv file to use on Excel. It will use the block's number as the Title.
                #f=open(str(latest_block)+'.csv','a+')
                # ------------------------------------------------------------------------------------------------------------
                # Write the information found to the .csv file
                #f.write(str(address)+"'\t"+str(value)+'\n')
                # ------------------------------------------------------------------------------------------------------
                # Close the .csv file when it is done.
                #f.close()
                # ----------------------------------------------------------------------------------------------------------------
            
            # My way of keeping memory usage to a minimum.
            #else:
                #value, address = 0, 0
                #continue
            
            # If you want to find a range, let's say from 6 - 6.5 bitcoins you would change the above loop on line 106 to:
            #if 6 <= value <=7:
            # -----------------------------------------------------------------------------------------------------------

        # If any errors are encountered the loop will just continue
        except:
            continue
        # ----------------------------------------------------------------------------------------------------------------

    # Get rid of all unnecessary information we've pulled so far before moving to the next block
    get_block_hash, blockhash, transactions, block, txid = 0, 0, 0, 0, 0
    # ---------------------------------------------------------------------------------------------------------------------

    # Go to the next lower block and print the number on screen.
    latest_block-=1
    print('\n' + str(latest_block))
