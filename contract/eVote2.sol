// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EVoting {
    uint256 public startVotingTime;
    uint256 public endVotingTime;
    address public admin;
    uint public totalVotes;

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin allowed");
        _;
    }

    // ✅ NEW: Track whether results have been published
    bool public resultsPublished = false;

    // ✅ NEW: Emit when results are published
    event ResultsPublished(uint timestamp);

    // Candidate registration per position
    mapping(uint => bytes32[]) public positionCandidates;

    // Vote counts per candidate per position
    mapping(uint => mapping(bytes32 => uint)) public voteCounts;

    // Tracks whether a voter has voted per position
    mapping(uint => mapping(bytes32 => bool)) public hasVoted;

    // Timestamps when voters cast votes
    mapping(uint => mapping(bytes32 => uint)) public voterTimestamps;

    function setVotingTime(uint _startVotingTime, uint _endVotingTime) public onlyAdmin {
        require(block.timestamp < _startVotingTime, "Start time must be in future");
        require(_endVotingTime > _startVotingTime, "End time must be after start time");
        startVotingTime = _startVotingTime;
        endVotingTime = _endVotingTime;
    }

    function extendVotingTime(uint _newEndTime) public onlyAdmin {
        require(block.timestamp < endVotingTime, "Voting already ended");
        require(_newEndTime > endVotingTime, "New end time must be later");
        endVotingTime = _newEndTime;
    }

    // Admin registers candidates per position (optional)
    function registerCandidate(uint positionId, bytes32 candidateHash) public onlyAdmin {
        positionCandidates[positionId].push(candidateHash);
    }

    function vote(uint positionId, bytes32 voterHash, bytes32 candidateHash) public {
        require(block.timestamp > startVotingTime, "Voting has not started");
        require(block.timestamp < endVotingTime, "Voting has ended");
        require(!hasVoted[positionId][voterHash], "Already voted for this position");

        // Optional: Enforce that candidate is registered for this position
        // bool valid = false;
        // for (uint i = 0; i < positionCandidates[positionId].length; i++) {
        //     if (positionCandidates[positionId][i] == candidateHash) {
        //         valid = true;
        //         break;
        //     }
        // }
        // require(valid, "Candidate not registered for this position");

        voteCounts[positionId][candidateHash]++;
        hasVoted[positionId][voterHash] = true;
        voterTimestamps[positionId][voterHash] = block.timestamp;
        totalVotes++;
    }

    function getVotes(uint positionId, bytes32 candidateHash) public view returns (uint) {
        require(block.timestamp > endVotingTime || msg.sender == admin, "Results not available yet");
        return voteCounts[positionId][candidateHash];
    }

    function getCandidates(uint positionId) public view returns (bytes32[] memory) {
        return positionCandidates[positionId];
    }

    function getVoterTimestamp(uint positionId, bytes32 voterHash) public view returns (uint) {
        return voterTimestamps[positionId][voterHash];
    }

    function getAdmin() public view returns (address) {
        return admin;
    }

    function getCurrentTimestamp() public view returns (uint) {
        return block.timestamp;
    }

    // ✅ NEW: Finalizes the results on-chain
    function publishResults() public onlyAdmin {
        require(block.timestamp > endVotingTime, "Voting still ongoing");
        require(!resultsPublished, "Already published");

        resultsPublished = true;
        emit ResultsPublished(block.timestamp);
    }

    function getVotingTime() public view returns (uint, uint) {
    return (startVotingTime, endVotingTime);
    }

}
