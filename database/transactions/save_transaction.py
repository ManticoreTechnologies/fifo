from utils import save_data_to_redis, get_data_from_redis

def save_transaction_to_redis(transaction):
    
    # Get the txid 
    txid = transaction['txid']

    # Save to the unconfirmed deposits list
    deposits = get_data_from_redis(f"deposits:unconfirmed")
    if deposits is None:
        deposits = []
    if txid not in deposits:
        deposits.append(txid)
    save_data_to_redis(f"deposits:unconfirmed", deposits)
    
    # Initialize the confirmations field to 0
    transaction['confirmations'] = 0

    # Map the transaction data to the txid
    save_data_to_redis(f"deposits:{txid}", transaction)

    

