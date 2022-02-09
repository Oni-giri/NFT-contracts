 // SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "../LightNonFungibleToken.sol";

contract MockLightNonFungibleToken is LightNonFungibleToken {
    constructor(string memory name_,
                string memory symbol_,
                uint256 collectionMaxItems_,
                uint256 maxMintsPerTx_,
                uint256 price_,
                uint256 startingTime_,
                uint256 maxWhitelistMint_,
                string memory _baseURI_,
                string memory _extensionURI_)
                LightNonFungibleToken(
                    name_,
                    symbol_,
                    collectionMaxItems_,
                    maxMintsPerTx_,
                    price_,
                    startingTime_,
                    maxWhitelistMint_,
                    _baseURI_,
                    _extensionURI_
                ){
                }


    function idToOwnerIndex(uint256 _id) external view returns(uint256) {
        return _idToOwnerIndex[_id];
    }

}