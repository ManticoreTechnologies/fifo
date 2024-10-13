# Test decodescript
from evrmore import decodescript
import json
from colorama import Fore, Style, init
from evrmore.transaction.decoderawtransaction import decoderawtransaction
from startup import calculate_block_hash, decode_block



# Initialize colorama
init(autoreset=True)

# Function to check if the data matches the actual data
def check_matching(data, actual_data):
    for key, value in data.items():
        if key not in actual_data or actual_data[key] != value:
            return False
    for key in actual_data:
        if key not in data:
            return False
    return True

# Function to pretty print JSON with colors, highlighting differences in red
def pretty_print_colored(data, actual_data, indent=0):
    matching = True
    indent_str = ' ' * indent
    print(indent_str + '{')
    # Print expected keys
    for i, (key, value) in enumerate(data.items()):
        # Set color to red if the key is missing in actual_data
        if key not in actual_data:
            key_color = Fore.RED 
            matching = False
        else:
            key_color = Fore.CYAN
        value_color = Fore.GREEN
        if key not in actual_data or actual_data[key] != value:
            value_color = Fore.RED
            matching = False
            
        print(indent_str + ' ' * 4 + key_color + json.dumps(key) + Style.RESET_ALL + ': ', end='')
        if isinstance(value, dict):
            pretty_print_colored(value, actual_data.get(key, {}), indent + 4)
        elif isinstance(value, list):
            print('[')
            for j, item in enumerate(value):
                if isinstance(item, dict):
                    pretty_print_colored(item, actual_data.get(key, [])[j] if j < len(actual_data.get(key, [])) else {}, indent + 8)
                else:
                    item_color = value_color if item not in actual_data.get(key, []) else Fore.GREEN
                    print(indent_str + ' ' * 8 + item_color + json.dumps(item) + Style.RESET_ALL, end='')
                if j < len(value) - 1:
                    print(',')
                else:
                    print()
            print(indent_str + ' ' * 4 + ']', end='')
        else:
            print(value_color + json.dumps(value) + Style.RESET_ALL, end='')
        if i < len(data) - 1:
            print(',')
        else:
            print()
    
    # Print unexpected keys in yellow
    for key in actual_data:
        if key not in data:
            print(indent_str + ' ' * 4 + Fore.YELLOW + json.dumps(key) + Style.RESET_ALL + ': ', end='')
            print(Fore.YELLOW + json.dumps(actual_data[key]) + Style.RESET_ALL)
            matching = False

    print(indent_str + '}', end='')
    return matching

# Function to run a single test case
def run_test_case(func, script, expected_output_file):
    decoded_script = func(script)
    expected_output = json.load(open(expected_output_file))
    
    # Check if the data matches
    matching = check_matching(expected_output, decoded_script)
    
    # Use the function to print the expected output, highlighting differences if not matching
    if not matching:
        pretty_print_colored(expected_output, decoded_script)
        print()
    
    # Print the result with the name of the test
    test_name = expected_output_file.split('/')[-1]  # Extract the file name from the path
    if matching:
        print(Fore.GREEN + f"Test '{test_name}': Matching: {matching}" + Style.RESET_ALL)
        return True
    else:
        print(f"Test '{test_name}': Matching: {matching}")
        return False

# List of test cases with function, script, and expected output file
test_cases = [

    # New asset
    (decodescript, "76a9146f00b7b316eacccb25e5840e8c4bdcaa8c07ac0888acc01a657672710a4d414e5449464f52474500e1f5050000000000010075", "test_data/scripts/new_asset.json"),
    # Transfer asset
    (decodescript, "76a91419b5dde0fa76f7febd02d04df10a1c66c1edfa1088acc017657672740a4d414e5449435241465400e1f5050000000075", "test_data/scripts/transfer_asset.json"),
    # Pubkeyhash
    (decodescript, "76a9144785cb52d0fafa1b77672f5d9b69db6083bd438988ac", "test_data/scripts/pubkeyhash.json"),
    # Scripthash
    (decodescript, "a9143ade040e5a03507435522b9d5542d6d063dcb1bb87", "test_data/scripts/scripthash.json"),
    # Reissue asset
    (decodescript, "76a9143c31c5bb776c15ba03f2fb88700c117b618e82de88acc036657672720558454e4f4e0076dd4101000000ff0112209ef32001260ce1d63225b4e42b03a3668d692deee2c736daaa1cbcc6e2c06de275", "test_data/scripts/reissue_asset.json"),
    # Null data
    (decodescript, "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9", "test_data/scripts/null_data.json"),
    # Nonstandard
    (decodescript, "4730440220579d3c0db1c9cf5b6b5b0f42eaa60149db3295273bc33c432bbc740935cbac29022037fed597faf759bae467b7932a5da2addaabd5f65dcd03b375d5b66621d135df012103507f4e0d43202acf10071aecc3dd9104bf5d3f406df42d117af310de56f135de", "test_data/scripts/nonstandard.json"),

    (decoderawtransaction, "0200000002717c1314538a094f6bb4fbe3e92b8edd87e772acb2201af511379ddd242f1f41000000006a4730440220579d3c0db1c9cf5b6b5b0f42eaa60149db3295273bc33c432bbc740935cbac29022037fed597faf759bae467b7932a5da2addaabd5f65dcd03b375d5b66621d135df012103507f4e0d43202acf10071aecc3dd9104bf5d3f406df42d117af310de56f135defeffffffb324b6adc39862efeab8f26ae3ca4bcea687e2e9322e3efbc048ff203a14c6ce020000006b483045022100b01f2b6c1249b302dd56f359e298178f57c4a410e0661307699cff609fa04ac002200e9c4e22ede5f236f9e2c4928861e22236905afb85a6debad96f3c45607c2dea012103ff787648ffbdcf44a64c56cc4e5f32572537a10327d64775c7d866e62ffcbad0feffffff0400e40b54020000001976a9149c8c16192e5fd0f278703982a5e50d97c2f2282688ac00000000000000002f76a914f75acf93906f8d4d96b83674cbd3d033050201a288acc013657672740658454e4f4e2100e1f5050000000075f0c486f0140000001976a914f75acf93906f8d4d96b83674cbd3d033050201a288ac00000000000000005276a9143c31c5bb776c15ba03f2fb88700c117b618e82de88acc036657672720558454e4f4e0076dd4101000000ff0112209ef32001260ce1d63225b4e42b03a3668d692deee2c736daaa1cbcc6e2c06de2756f910f00", "test_data/transactions/example1.json"),

    (calculate_block_hash, "000000307d4106ba8b750df41f9dbf399011adf4941024b994b17002383a1400000000005efd5d1b73d7dd6bb61ec1039ba5aa1132e12b566f0891b0ea8e5ae7c1ea9f4f95150a670b0d261ba08c0f0005cba92100c0d39020aff1d605cbd408e2bc64743a8884122362fc8a821602a13d04d37d85fbab9d01010000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff1d03a08c0f0495150a670290d3102f436f696e4d696e65727a2e636f6d2f0000000005c06a54a1390000001976a9144785cb52d0fafa1b77672f5d9b69db6083bd438988ac0029d1770600000017a9143ade040e5a03507435522b9d5542d6d063dcb1bb872003834a000000001976a9149d35fa99ee8516bf88a2683ad6f50979fc0a923f88ac2003834a000000001976a914a4f67ca4f9c05ed30b3f510a18e15bde9090d49588ac0000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf90120000000000000000000000000000000000000000000000000000000000000000000000000", "test_data/blocks/hash/example1.json"),

    (decode_block, "000000307d4106ba8b750df41f9dbf399011adf4941024b994b17002383a1400000000005efd5d1b73d7dd6bb61ec1039ba5aa1132e12b566f0891b0ea8e5ae7c1ea9f4f95150a670b0d261ba08c0f0005cba92100c0d39020aff1d605cbd408e2bc64743a8884122362fc8a821602a13d04d37d85fbab9d01010000000001010000000000000000000000000000000000000000000000000000000000000000ffffffff1d03a08c0f0495150a670290d3102f436f696e4d696e65727a2e636f6d2f0000000005c06a54a1390000001976a9144785cb52d0fafa1b77672f5d9b69db6083bd438988ac0029d1770600000017a9143ade040e5a03507435522b9d5542d6d063dcb1bb872003834a000000001976a9149d35fa99ee8516bf88a2683ad6f50979fc0a923f88ac2003834a000000001976a914a4f67ca4f9c05ed30b3f510a18e15bde9090d49588ac0000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf90120000000000000000000000000000000000000000000000000000000000000000000000000", "test_data/blocks/example2.json")
    # decoderawtransaction 0200000002717c1314538a094f6bb4fbe3e92b8edd87e772acb2201af511379ddd242f1f41000000006a4730440220579d3c0db1c9cf5b6b5b0f42eaa60149db3295273bc33c432bbc740935cbac29022037fed597faf759bae467b7932a5da2addaabd5f65dcd03b375d5b66621d135df012103507f4e0d43202acf10071aecc3dd9104bf5d3f406df42d117af310de56f135defeffffffb324b6adc39862efeab8f26ae3ca4bcea687e2e9322e3efbc048ff203a14c6ce020000006b483045022100b01f2b6c1249b302dd56f359e298178f57c4a410e0661307699cff609fa04ac002200e9c4e22ede5f236f9e2c4928861e22236905afb85a6debad96f3c45607c2dea012103ff787648ffbdcf44a64c56cc4e5f32572537a10327d64775c7d866e62ffcbad0feffffff0400e40b54020000001976a9149c8c16192e5fd0f278703982a5e50d97c2f2282688ac00000000000000002f76a914f75acf93906f8d4d96b83674cbd3d033050201a288acc013657672740658454e4f4e2100e1f5050000000075f0c486f0140000001976a914f75acf93906f8d4d96b83674cbd3d033050201a288ac00000000000000005276a9143c31c5bb776c15ba03f2fb88700c117b618e82de88acc036657672720558454e4f4e0076dd4101000000ff0112209ef32001260ce1d63225b4e42b03a3668d692deee2c736daaa1cbcc6e2c06de2756f910f00
    # Add more test cases with different functions here
]

# Initialize a counter for successful tests
successful_tests = 0

# Run through each test case and stop if one fails
for func, script, expected_output_file in test_cases:
    if run_test_case(func, script, expected_output_file):
        successful_tests += 1
    else:
        print(f"Test failed for script: {script}")
        break

# Print the number of successful tests
print(Fore.CYAN + f"Number of successful tests: {successful_tests}/{len(test_cases)}" + Style.RESET_ALL)
