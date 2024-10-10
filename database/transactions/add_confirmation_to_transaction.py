from utils import get_data_from_redis, save_data_to_redis


# Adds a confirmation to a transaction and moves it from the unconfirmed to the confirmed list
def add_confirmation_to_transaction(transaction):
    # Get the txid
    txid = transaction['txid']

    # Get the transaction from redis
    transaction = get_data_from_redis(f"deposits:{txid}")

    # Add the confirmation to the transaction
    transaction['confirmations'] += 1

    # Remove the transaction from the unconfirmed deposits list
    print(f"Removing {txid} from unconfirmed deposits list")
    deposits = get_data_from_redis(f"deposits:unconfirmed")
    if deposits is not None and txid in deposits:
        deposits.remove(txid)
        save_data_to_redis(f"deposits:unconfirmed", deposits)
    
    # Add the transaction to the confirmed deposits list
    print(f"Adding {txid} to confirmed deposits list")
    deposits = get_data_from_redis(f"deposits:confirmed")
    if deposits is None:
        deposits = []
    if txid not in deposits:
        deposits.append(txid)
    save_data_to_redis(f"deposits:confirmed", deposits)

    # Save the transaction to redis
    save_data_to_redis(f"deposits:{txid}", transaction)

