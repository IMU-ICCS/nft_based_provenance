// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./node_modules/@openzeppelin/contracts/token/ERC721/extensions/ERC721Enumerable.sol";
import "./node_modules/@openzeppelin/contracts/access/Ownable.sol";

contract DatasetNFT is ERC721Enumerable, Ownable {
    struct Dataset {
        address uploader;
        Evaluation evaluation;
        address[3] evaluatorAddresses; // Array of evaluator addresses
    }

    struct Evaluation {
        bool not_nulls;
        uint256 rows;
        uint256 score1;
    }

    struct Evaluator {
        uint8 attributeIndex;
        address evaluatorAddress;
        bool is_active;
    }

    Evaluator[] public evaluators;
    Dataset[] public datasets1;


    address public chairperson;
    uint256 public datasetCount = 0;

    mapping(uint256 => Dataset) public datasets;
    mapping(uint256 => Evaluation) public evaluations;
    mapping(address => uint256) public evaluatorIndexByAddress;



    // Define events to emit
    event DatasetAdded(uint256 indexed datasetId, address indexed uploader);
    event NotNullsSet(address indexed evaluatorAddress, uint256 indexed datasetId, bool newValue);
    event Score1Set(address indexed evaluatorAddress, uint256 indexed datasetId, uint256 newValue);
    event RowsSet(address indexed evaluatorAddress, uint256 indexed datasetId, uint256 newValue);
    event NFTMinted(uint256 indexed datasetId, address indexed minter);
    event EvaluatorActivated(address indexed evaluatorAddress);
    event EvaluatorDeactivated(address indexed evaluatorAddress);
    event DebugLog(address indexed evaluatorAddress);


    constructor() ERC721("DatasetNFT", "DNFT") {
        chairperson=msg.sender;
    }

    modifier has_3_Evaluators(uint256 datasetId) {
        require(datasets[datasetId].evaluatorAddresses.length == 3, "Insufficient evaluations");
        _;
    }


    function addEvaluator(
        uint8 _attributeIndex,
        address _evaluatorAddress
    ) external onlyOwner {
        require(_evaluatorAddress != address(0), "Invalid evaluator address");    
        Evaluator memory newEvaluator = Evaluator({
            attributeIndex: _attributeIndex,
            evaluatorAddress: _evaluatorAddress,
            is_active: false
        });
        evaluators.push(newEvaluator);
        uint256 newIndex = evaluators.length - 1; // Get the index of the newly added evaluator
        evaluatorIndexByAddress[_evaluatorAddress] = newIndex;
    }

        // Function to activate an evaluator
    function activateEvaluator(address _evaluatorAddress) external onlyOwner {
        Evaluator storage evaluator = evaluators[evaluatorIndexByAddress[_evaluatorAddress]];
        require(evaluator.evaluatorAddress != address(0), "Evaluator not found");
        require(evaluator.evaluatorAddress != address(0) && evaluator.is_active==false , "Evaluator is already active");
        evaluators[evaluatorIndexByAddress[_evaluatorAddress]].is_active=true;
        // Activate the evaluator
        evaluator.is_active = true;
        emit EvaluatorActivated(_evaluatorAddress);
    }

    // Function to deactivate an evaluator
    function deactivateEvaluator(address evaluatorAddress) external onlyOwner {
        Evaluator storage evaluator = evaluators[evaluatorIndexByAddress[evaluatorAddress]];
        require(evaluator.evaluatorAddress != address(0), "Evaluator not found");
        require(evaluator.evaluatorAddress != address(0) && evaluators[evaluatorIndexByAddress[evaluatorAddress]].is_active==true , "Evaluator is already inactive");
        evaluators[evaluatorIndexByAddress[evaluatorAddress]].is_active=false;
        // Deactivate the evaluator
        evaluator.is_active = false;
        emit EvaluatorDeactivated(evaluatorAddress);
    }



    function getAllEvaluators() public view returns (Evaluator[] memory) {
        return evaluators;
    }

    
    function getEvaluatorAddresses(uint256 datasetId) public view returns (address[3] memory) {
        return datasets[datasetId].evaluatorAddresses;
    }


    //Function to Get Datasets by Uploader:
    function getDatasetsByUploader(address uploader) external view returns (Dataset[] memory) {
        uint256 uploaderDatasetCount = 0;
        for (uint256 i = 0; i < datasetCount; i++) {
            if (datasets[i].uploader == uploader) {
                uploaderDatasetCount++;
            }
        }
        Dataset[] memory result = new Dataset[](uploaderDatasetCount);
        uint256 resultIndex = 0;
        for (uint256 i = 0; i < datasetCount; i++) {
            if (datasets[i].uploader == uploader) {
                result[resultIndex] = datasets[i];
                resultIndex++;
            }
        }
        return result;
    }





    
    function addDataset() external {
        uint256 newDatasetId = datasetCount;
        // Create a new Dataset struct
        Dataset storage newDataset = datasets[newDatasetId];
        newDataset.uploader = msg.sender;
        // Initialize the evaluatorAddresses array within the struct
        newDataset.evaluatorAddresses[0] = address(0);
        newDataset.evaluatorAddresses[1] = address(0);
        newDataset.evaluatorAddresses[2] = address(0);
        // Create a new Evaluation struct
        Evaluation storage newEvaluation = evaluations[newDatasetId];
        newEvaluation.not_nulls = false;
        newEvaluation.score1 = 0;
        newEvaluation.rows = 0;
        // Increment the datasetCount for the next dataset
        datasetCount++;
        emit DatasetAdded(newDatasetId, msg.sender);
    }


    function set_not_nulls(address evaluatorAddress, bool newValue, uint256 datasetId) external {
    // Ensure that the evaluator with this address exists and has attribute index 1
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].evaluatorAddress == evaluatorAddress, "Evaluator not found");
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].attributeIndex == 0, "Evaluator is not allowed to set not_nulls");
        // Ensure that the dataset exists
        require(datasetId < datasetCount, "Dataset not found");

        // Get the corresponding Evaluation struct for the dataset
        Dataset storage dataset = datasets[datasetId];
        Evaluation storage eval = evaluations[datasetId];
        dataset.evaluation.not_nulls = newValue;
         // Find the first null index
        uint8 nullIndex = 0;
        while (nullIndex < 3 && dataset.evaluatorAddresses[nullIndex] != address(0)) {
            nullIndex++;
        }
        
        // Ensure that there is a null index available
        require(nullIndex < 3, "No null index available");

        // Replace the evaluator address at the null index
        dataset.evaluatorAddresses[nullIndex] = evaluatorAddress;
        // Update the first boolean value
        eval.not_nulls = newValue;
        emit NotNullsSet(evaluatorAddress, datasetId, newValue);
    }

    function set_score1(address evaluatorAddress, uint256 newValue, uint256 datasetId) external {
    // Ensure that the evaluator with this address exists and has attribute index 1
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].evaluatorAddress == evaluatorAddress, "Evaluator not found");
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].attributeIndex == 2, "Evaluator is not allowed to set score_1");
        // Ensure that the dataset exists
        require(datasetId <= datasetCount, "Dataset not found");
        // Get the corresponding Evaluation struct for the dataset

        Dataset storage dataset = datasets[datasetId];
        Evaluation storage eval = evaluations[datasetId];
        // Check that float1 is currently blank (0) before updating it
        require(eval.score1 == 0, "Score1 is already set");
        // Update float1
        dataset.evaluation.score1 = newValue;

         // Find the first null index
        uint8 nullIndex = 0;
        while (nullIndex < 3 && dataset.evaluatorAddresses[nullIndex] != address(0)) {
            nullIndex++;
        }
        
        // Ensure that there is a null index available
        require(nullIndex < 3, "No null index available");

        // Replace the evaluator address at the null index
        dataset.evaluatorAddresses[nullIndex] = evaluatorAddress;
        emit Score1Set(evaluatorAddress, datasetId, newValue);
    }

    function set_rows(address evaluatorAddress, uint256 newValue, uint256 datasetId) external {
    // Ensure that the evaluator with this address exists and has attribute index 1
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].evaluatorAddress == evaluatorAddress, "Evaluator not found");
        require(evaluators[evaluatorIndexByAddress[evaluatorAddress]].attributeIndex == 1, "Evaluator is not allowed to set number of rows");
        // Ensure that the dataset exists
        require(datasetId < datasetCount, "Dataset not found");
        // Get the corresponding Evaluation struct for the dataset
        Dataset storage dataset = datasets[datasetId];
        Evaluation storage eval = evaluations[datasetId];
        // Check that rows is currently blank (0) before updating it
        require(eval.rows == 0, "Raw's attribute already set");
        // Update float1
        dataset.evaluation.rows = newValue;

         // Find the first null index
        uint8 nullIndex = 0;
        while (nullIndex < 3 && dataset.evaluatorAddresses[nullIndex] != address(0)) {
            nullIndex++;
        }
        
        // Ensure that there is a null index available
        require(nullIndex < 3, "No null index available");

        // Replace the evaluator address at the null index
        dataset.evaluatorAddresses[nullIndex] = evaluatorAddress;
        eval.rows = newValue;
        emit RowsSet(evaluatorAddress, datasetId, newValue);
    }

    function mintNFTForDataset(uint256 datasetId,address minter) external {
        require(datasetId < datasetCount, "Dataset not found");   
        Dataset storage dataset = datasets[datasetId];
        // Ensure that the caller is the uploader of the dataset
        emit DebugLog(dataset.uploader);
        emit DebugLog(minter);
        //require(dataset.uploader == msg.sender, "Only the uploader can mint the NFT");
        // Ensure that the dataset has exactly 3 evaluators
        require(dataset.evaluatorAddresses.length == 3, "Dataset must have 3 evaluators to mint an NFT");      
        // Mint the NFT (you should implement your NFT minting logic here)
        _mint(minter, datasetId);
        // After minting the NFT,emit event
        emit NFTMinted(datasetId, minter);
    }

    function getChairPerson()public view returns(address) {
        return chairperson;
  }
}
