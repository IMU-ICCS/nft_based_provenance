from flask import Flask,jsonify,render_template, request,redirect
import os
from flask_bootstrap import Bootstrap5
from eth_utils import to_hex
import json
from hexbytes import HexBytes
from web3 import Web3
import solcx
import json
from solcx import compile_files, compile_source
from forms import *
import threading
from flask_socketio import SocketIO
import time



solcx.install_solc(version='0.8.9')
solcx.set_solc_version('0.8.9')

eth_rpc_url = "http://localhost:7545"

# Connect to a local or remote Ethereum node
w3 = Web3(Web3.HTTPProvider(eth_rpc_url))

with open("lighter.sol", "r") as file:
    contract_source_code = file.read()


# Compile the contract
compiled_sol = compile_source(contract_source_code)

# Extract the contract ABI and bytecode
contract_interface = compiled_sol['<stdin>:DatasetNFT']

# Write compiled smart contract as JSON.
with open("compiled_sol.json", "w") as file:
    json.dump(compiled_sol, file)

# Deploy the contract
def deploy_contract():
    
    private_key = " Replace with your Ethereum account's private key 

    # Define the contract owner's address (replace with your actual address)
    owner_address = "0xfB5A54CAF08AD750caC99d7a0710A6a575a091cB"

    # Create a contract instance
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Build the transaction
    nonce = w3.eth.get_transaction_count(owner_address)
    gas_price = w3.to_wei('20', 'gwei')  # Replace with an appropriate gas price
    gas_limit = 6721975    # Replace with an appropriate gas limit

    transaction = {
        'nonce': nonce,
        'gasPrice': gas_price,
        'gas': gas_limit,
        'from': owner_address,
        'data': contract_interface['bin']
    }

    # Sign and send the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)

    # Wait for the transaction to be mined
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    # Extract the deployed contract's address
    contract_address = receipt['contractAddress']

    return contract_address



contract_address = deploy_contract()
print(f"Contract deployed at address: {contract_address}")
contract = w3.eth.contract(address=contract_address, abi=contract_interface['abi'])





app = Flask(__name__,static_url_path='/static')
app.config['SECRET_KEY'] = 'TempSecretKey'
socketio = SocketIO(app)
BOOTSTRAP = Bootstrap5(app)


def handle_evaluator_activated(event):
    print("Evaluator Activated:")
    print("Evaluator Address:", event['args']['evaluatorAddress'])
    # code to handle the event here
    evaluator_address = event['args']['evaluatorAddress']
    socketio.emit('evaluator_activated', {'evaluator_address': evaluator_address})

def handle_evaluator_deactivated(event):
    print("Evaluator Deactivated:")
    print("Evaluator Address:", event['args']['evaluatorAddress'])
    # code to handle the event here
    evaluator_address = event['args']['evaluatorAddress']
    socketio.emit('evaluator_deactivated', {'evaluator_address': evaluator_address})


def handle_dataset_added(event):
    print("Dataset Added:")
    print("Uploader Address:", event['args']['uploader'])
    print("DatasetId ", event['args']['datasetId'])

    # code to handle the event here
    uploader = event['args']['uploader']
    dataset_id= event['args']['datasetId']
    socketio.emit('dataset_added', {'uploader': uploader, 'datasetId':dataset_id})
    set_not_nulls(dataset_id)
    set_rows(dataset_id)

def handle_not_nulls_set(event):
    evaluatorAddress = event['args']['evaluatorAddress']
    datasetId= event['args']['datasetId']
    new_value= event['args']['newValue']
    socketio.emit('not_null_set', {'evaluatorAddress': evaluatorAddress, 'datasetId':datasetId,'new_value':new_value})

def handle_score1_set(event):
    evaluatorAddress = event['args']['evaluatorAddress']
    datasetId= event['args']['datasetId']
    new_value= event['args']['newValue']
    socketio.emit('score1_set', {'evaluatorAddress': evaluatorAddress, 'datasetId':datasetId,'new_value':new_value})    

def handle_rows_set(event):
    evaluatorAddress = event['args']['evaluatorAddress']
    datasetId= event['args']['datasetId']
    new_value= event['args']['newValue']
    socketio.emit('rows_set', {'evaluatorAddress': evaluatorAddress, 'datasetId':datasetId,'new_value':new_value})      

def handle_nft_minted(event):
    datasetId= event['args']['datasetId']
    minter= event['args']['minter']
    socketio.emit('nft_minted', {'minter': minter, 'datasetId':datasetId})  

def handle_debug(event):
    try:
        print("------------check------------")
        evaluatorAddress = event['args']['evaluatorAddress']
        print(evaluatorAddress)
    except Exception as e:
        print("An error occurred:", e)



def event_listener():
    # Create event filters for all the events
    event_filter_activated = contract.events.EvaluatorActivated.create_filter(fromBlock='latest')
    event_filter_deactivated = contract.events.EvaluatorDeactivated.create_filter(fromBlock='latest')
    event_filter_dataset_added = contract.events.DatasetAdded.create_filter(fromBlock='latest')
    event_filter_not_nulls_set = contract.events.NotNullsSet.create_filter(fromBlock='latest')
    event_filter_score1_set = contract.events.Score1Set.create_filter(fromBlock='latest')
    event_filter_rows_set = contract.events.RowsSet.create_filter(fromBlock='latest')
    event_filter_nft_minted = contract.events.NFTMinted.create_filter(fromBlock='latest')
    event_filter_debug = contract.events.DebugLog.create_filter(fromBlock='latest')
    

    while True:
        for event in event_filter_activated.get_new_entries():
            handle_evaluator_activated(event)

        for event in event_filter_deactivated.get_new_entries():
            handle_evaluator_deactivated(event)

        for event in event_filter_dataset_added.get_new_entries():
            handle_dataset_added(event)

        for event in event_filter_not_nulls_set.get_new_entries():
            handle_not_nulls_set(event)

        for event in event_filter_score1_set.get_new_entries():
            handle_score1_set(event)

        for event in event_filter_rows_set.get_new_entries():
            handle_rows_set(event)

        for event in event_filter_nft_minted.get_new_entries():
            handle_nft_minted(event)
            
        for event in event_filter_debug.get_new_entries():
            handle_debug(event)


# Start the event listener in a separate thread
event_thread = threading.Thread(target=event_listener)
event_thread.daemon = True
event_thread.start()

def set_not_nulls(dataset_id):
    socketio.sleep(3)
    # Define the evaluator address (replace with 2nd address of ganache)
    private_key = "0xa343948a2acb6f0721783dceebe83853f5635cdb8a252d23e711781ab4a209e4"

    # Define the evaluator address (replace with 2nd address of ganache)
    owner_address = "0x9DA2FDCa4A1B2e75A6dB6a6c16BA0DdC3f328B7E"

    # Create a contract instance
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Build the transaction
    nonce = w3.eth.get_transaction_count(owner_address)
    gas_price = w3.to_wei('20', 'gwei')  # Replace with an appropriate gas price
    gas_limit = 6721975    # Replace with an appropriate gas limit
    transaction =  contract.functions.set_not_nulls(w3.eth.accounts[1], True, dataset_id).build_transaction({'chainId': 1337,'from': w3.eth.accounts[1],'to':contract_address,'nonce': nonce,'gasPrice': gas_price,'gas': 6721975, })


    # Sign the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    #print(receipt)


def set_rows(dataset_id):
    socketio.sleep(3)
    # Define the evaluator address (replace with 2nd address of ganache)
    private_key = "0x8c44240e676869fc2c603470a85b260810819917af1c941b0a0e40bc2587b58d"

    # Define the evaluator address (replace with 2nd address of ganache)
    owner_address = "0x274649326CCb40df1F121C3E9b7684999Ed56659"

    # Create a contract instance
    contract = w3.eth.contract(abi=contract_interface['abi'], bytecode=contract_interface['bin'])

    # Build the transaction
    nonce = w3.eth.get_transaction_count(owner_address)
    gas_price = w3.to_wei('20', 'gwei')  # Replace with an appropriate gas price
    gas_limit = 6721975    # Replace with an appropriate gas limit
    transaction =  contract.functions.set_rows(w3.eth.accounts[2], 99, dataset_id).build_transaction({'chainId': 1337,'from': w3.eth.accounts[2],'to':contract_address,'nonce': nonce,'gasPrice': gas_price,'gas': 6721975, })


    # Sign the transaction
    signed_transaction = w3.eth.account.sign_transaction(transaction, private_key)

    # Send the transaction
    tx_hash = w3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    #print(receipt)




@app.route("/")
def home():
    print(contract_address)

    form = AddEvaluatorForm()
    form1=EvaluateForm()
    form2=FileForm()
    form.evaluatorAddress.choices = []

    i=0
    for chooseaccount in w3.eth.accounts:
        i+=1
        form.evaluatorAddress.choices += [(chooseaccount, chooseaccount)]

    with open("compiled_sol.json", "r") as file:
        data=json.load(file)

    if form2.validate_on_submit():
        f = form2.file.data
        filename = secure_filename(f.filename)
        f.save(os.path.join(
            app.instance_path, 'photos', filename
        ))
        return redirect(url_for('home'))

    


    return render_template(
        'home.jinja2',
        contract_address=contract_address,
        jsonInterface=data["<stdin>:DatasetNFT"]['abi'],
        abi=contract_interface['abi'],
        form=form,
        form1=form1,
        form2=form2
    )

@app.route("/admin")
def admin():
    return render_template(
        'admin.jinja2',
        contract_address=contract_address,
        jsonInterface=contract_interface['bin'],
        abi=contract_interface['abi']
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    # Get the uploaded file
    uploaded_file = request.files['file']

    # Check if the file exists and save it to the upload folder
    if uploaded_file:
        uploaded_file.save('upload_folder/' + 'new_filename.ext')

    return 'File uploaded successfully'

@app.route("/documentation")
def documentation():
    print(contract_address)
    return render_template(
        'documentation.html'
    )


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
