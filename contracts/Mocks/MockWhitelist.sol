 // SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../Whitelist.sol";

contract MockWhitelist is Whitelist {
    function setSigner(address signer) public {
        _signer = signer;
    }


    function getMessageHash(address _to, uint256 _amount, uint256 _price) public pure returns (bytes32) {
        return _getMessageHash(_to, _amount, _price);
    }


    function getEthSignedMessageHash(bytes32 _messageHash) public pure returns (bytes32) {
        return _getEthSignedMessageHash(_messageHash);
    }


    function verify(address _to, uint256 _amount, uint256 _price, bytes memory _signature) public view returns (bool) {
        return _verify(_to, _amount, _price, _signature);
    }


    function recoverSigner(bytes32 _ethSignedMessageHash, bytes memory _signature) public pure returns (address) {
        return _recoverSigner(_ethSignedMessageHash, _signature);
    }
}